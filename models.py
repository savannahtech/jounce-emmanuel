from sqlalchemy import Column, Integer, Float, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class LLMPerformance(Base):
    __tablename__ = "llm_performance"
    id = Column(Integer, primary_key=True, index=True)
    llm_name = Column(String, index=True)
    metric_name = Column(String, index=True)
    value = Column(Float)
