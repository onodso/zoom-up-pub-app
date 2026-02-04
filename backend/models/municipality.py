from sqlalchemy import Column, Integer, String, Text, DateTime, Float, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Municipality(Base):
    __tablename__ = "municipalities"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(6), unique=True, nullable=False)
    prefecture = Column(String(10), nullable=False, index=True)
    name = Column(String(50), nullable=False)
    region = Column(String(10), nullable=False, index=True)
    population = Column(Integer, default=0)
    households = Column(Integer, default=0)
    mayor_name = Column(String(50), nullable=True)
    official_url = Column(Text, nullable=True)
    contact_phone = Column(String(20), nullable=True)
    contact_email = Column(String(100), nullable=True)
    score_total = Column(Float, nullable=True, default=0.0, index=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
