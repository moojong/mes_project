from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector
from core.database import Base

class Vector(Base):
    __tablename__ = "vectors"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String, index=True)  # 문서 이름 등
    content = Column(Text, nullable=False)
    embedding = Column(Vector(768))  # nomic-embed-text용 768차원 벡터