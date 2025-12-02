
import torch
import os
import dotenv
from openai import OpenAI
from google import genai
import requests
import json
from transformers import pipeline

dotenv.load_dotenv()

os.environ['HF_TOKEN'] = os.getenv("huggingface_api_key")
model_id = "meta-llama/Llama-3.2-1B-Instruct"

openai_client = OpenAI(api_key=os.getenv("chatgpt_api_key"))
gemini_client = genai.Client(api_key=os.getenv("gamini_api_key"))

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