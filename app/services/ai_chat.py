
import torch
import os
import dotenv
from openai import OpenAI
from google import genai
import requests
import json
from transformers import pipeline

import tempfile
from fastapi import UploadFile
from models.vector import Vector
from sqlalchemy import text
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import inspect, text

import fitz # PyMuPDF

dotenv.load_dotenv()

os.environ['HF_TOKEN'] = os.getenv("huggingface_api_key")
model_id = "meta-llama/Llama-3.2-1B-Instruct"

openai_client = OpenAI(api_key=os.getenv("chatgpt_api_key"))
gemini_client = genai.Client(api_key=os.getenv("gamini_api_key"))

# Ollama 임베딩 설정
OLLAMA_BASE_URL = "http://ollama:11434"
EMBEDDING_MODEL = "nomic-embed-text"  # 768차원

def get_ollama_embedding(text: str) -> list[float]:
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=30
        )
        response.raise_for_status()
        embedding = response.json()['embedding']
        return embedding
    except Exception as e:
        print(f"[ERROR] Ollama 임베딩 생성 실패: {str(e)}")
        raise

def load_pdf(filepath: str) -> str:
    text = ""
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    return text.strip()

def load_pdf_by_paragraph(filepath: str) -> list[str]:
    full_text = load_pdf(filepath)
    # 연속 줄바꿈을 기준으로 분리하고, 너무 짧은 문단은 제외
    import re
    paragraphs = re.split(r'\n\s*\n', full_text)
    return [p.strip() for p in paragraphs if p.strip()]

def embed_text(text: str) -> list[float]:
    return model.encode(text).tolist()

def embed_pdf_to_vectors(file_path: str) -> tuple[list[str], list[list[float]]]:
    paragraphs = load_pdf_by_paragraph(file_path)
    vectors = []
    for idx, paragraph in enumerate(paragraphs):
        try:
            vector = get_ollama_embedding(paragraph)
            vectors.append(vector)
        except Exception as e:
            print(f"[ERROR] 문단 {idx + 1} 임베딩 실패: {str(e)}")
            continue
    
    print(f"[INFO] 임베딩 완료: {len(vectors)}개 벡터 생성")
    return paragraphs[:len(vectors)], vectors # 임베딩 실패한 문단 제외

async def process_document_and_store_vectors(db: Session, upload_file: UploadFile) -> str:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            contents = await upload_file.read()
            tmp.write(contents)
            tmp_path = tmp.name

        # 문단별 텍스트와 벡터 리스트 추출
        texts, vectors = embed_pdf_to_vectors(tmp_path)
        print(f"[DEBUG] 문단 수: {len(texts)}")
        
        for idx, (text, vector) in enumerate(zip(texts, vectors)):
            print(f"[DEBUG] 저장 중: 문단 {idx + 1} - 길이 {len(text)}")
            doc_vector = Vector(
                content=text,
                embedding=vector
            )
            db.add(doc_vector)
            
        db.commit()
        os.unlink(tmp_path) # 임시 파일 삭제
        
        return f"Successfully stored {len(vectors)} vectors."
    
    except SQLAlchemyError as e:
        db.rollback()
        return f"Database error: {str(e)}"
    except Exception as e:
        return f"Error occurred: {str(e)}"

def generate_rag_response(db: Session, user_input: str, model: str) -> str:
    try:
        # 벡터 DB에서 유사 문서 검색
        query_vector = get_ollama_embedding(user_input)
        results = db.query(
            Vector.content,
            Vector.embedding.cosine_distance(query_vector).label('distance')
        ).order_by('distance').limit(2).all()

        context = "\n\n".join([row.content for row in results])
        prompt = f"다음 문서를 참고하여 질문에 답변해 주세요:\n\n{context}\n\n질문: {user_input}"
        
        messages = [
            {"role": "system", "content":  "당신은 주어진 문서(context)를 기반으로만 답변하는 어시스턴트입니다. "
                    "반드시 한국어로만 답변하세요. 문서에 없는 내용은 추측하지 말고 "
                    "'해당 문서에서 답을 찾을 수 없습니다.'라고 답변하세요."},
            {"role": "user", "content": prompt}
        ]
        print(model)
        responses = pipe(
            messages,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
        )

        reply = responses[0]['generated_text'][-1]['content']
        
        # 원본 프롬프트 제거
        if prompt in reply:
            reply = reply.replace(prompt, "").strip() 
        
        return reply
    
    except Exception as e:
        print(f"Error in RAG response generation: {str(e)}")
        return f"Error: {str(e)}"
    
def get_database_schema(db: Session) -> str:
    # 현재 연결된 데이터베이스의 모든 테이블과 컬럼 정보를 텍스트로 추출
    inspector = inspect(db.bind)
    table_names = inspector.get_table_names()
    
    schema_info = []
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        # 컬럼명과 타입 정보를 문자열로 변환
        col_strings = [f"{col['name']} ({col['type']})" for col in columns]
        schema_info.append(f"Table: {table_name}\nColumns: {', '.join(col_strings)}")
    
    return "\n\n".join(schema_info)
    
def generate_sql_from_text(db: Session, query: str, model: str) -> str:
    schema = get_database_schema(db)
    
    system_prompt = f"""
    You are a PostgreSQL expert. Given an input question, create a syntactically correct PostgreSQL query to run.
    Here is the database schema:
    {schema}
    
    Rules:
    1. Only return the SQL query. Do not add markdown blocks.
    2. Use only SELECT statements.
    """
    
    user_prompt = f"Question: {query}\nSQL Query:"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]

    # 모델별 분기 처리
    if model == "gpt":
        return generate_gpt_chat_response(messages)
    elif model == "gemini":
        return generate_gemini_chat_response(messages)
    elif model in ["qwen2.5:7b", "gemma3:4b"]:
        return generate_local_llm_chat_response(model, messages)
    return "Invalid model selected."

def execute_generated_sql(db: Session, sql: str) -> dict:
    try:
        # SELECT 문만 허용
        if not sql.strip().upper().startswith("SELECT"):
            return {"error": "Only SELECT queries are allowed."}

        # SQL 실행
        result = db.execute(text(sql))
        columns = result.keys()
        rows = result.fetchall()
        
        return {
            "columns": list(columns),  # HTML의 <th>
            "rows": rows,              # HTML의 <tbody>
            "success": True
        }
    except Exception as e:
        return {"error": str(e), "success": False}

def generate_gpt_chat_response(messages: list[dict]) -> str:
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error occurred: {str(e)}"

def generate_gemini_chat_response(messages: list[dict]) -> str:
    try:
        response = gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=messages[0]['content'],
        )
        return response.text
    except Exception as e:
        return f"Error occurred: {str(e)}"

pipe = pipeline(
    "text-generation",
    model=model_id,
    dtype=torch.bfloat16,
    device_map="auto",
)

def generate_local_llm_chat_response(model: str, messages: list[dict]) -> str:
    try:
        url = "http://ollama:11434/api/chat"
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0.7,
            "stream": False
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        response = response.json()  
        content = response.get("message", {}).get("content", "")
        return content
        
    except Exception as e:
        return f"Error occurred: {str(e)}"

def generate_response(data: dict):
    prompt = data.get("message", "")
    
    messages = [
        {"role": "system", "content": "You are a helpful assistant. Always respond in Korean only. 한국어로만 답변하세요."},
        {"role": "user", "content": prompt}
    ]
    try:
        responses = pipe(
            #prompt,
            messages,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.9,
            repetition_penalty=1.2,
            do_sample=True,
            # num_return_sequences=3
        )
        print(f"Full response: {responses}")
        #reply = responses[0]['generated_text']
        reply = responses[0]['generated_text'][-1]['content']
        
        # 원본 프롬프트 제거
        if prompt in reply:
            reply = reply.replace(prompt, "").strip() 
        
        return reply
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}"