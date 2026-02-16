from sqlalchemy import Column, String, Integer, Float, Date, DateTime, Text, BigInteger
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime
from database import Base # Assuming Base = declarative_base() is in database.py

class Tender(Base):
    __tablename__ = "tenders"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Basic Info
    title = Column(Text, nullable=False)
    source_id = Column(String, index=True) # e.g. KKJ ResultId or Key
    source_url = Column(Text)
    
    # Agency / Location
    agency_name = Column(String) # 発注機関名
    municipality_id = Column(String, index=True) # 自治体コード (e.g. 29201)
    mesh_code = Column(String, index=True) # 開催場所等のメッシュ (Optional)
    
    # Dates
    published_date = Column(Date) # 公示日
    closing_date = Column(Date)   # 入札締切日
    awarded_date = Column(Date)   # 落札日
    
    # Result Info (Optional)
    winner_name = Column(String)
    winner_corporate_number = Column(String, index=True) # Company.corporate_number FK
    contract_amount = Column(BigInteger)
    
    # Classification & Sales Logic
    category = Column(String) # 旧カテゴリ (IT/DX)
    suggested_pattern = Column(String, index=True) # Sales Playbook Pattern (e.g. "ZP + AI Concierge")
    sales_status = Column(String, default="Lead") # Lead, Approach, Closed
    
    # Metadata
    api_source = Column(String) # "KKJ", "P-PORTAL", "MANUAL"
    raw_data = Column(Text) # JSON string of raw API response specific fields
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Tender(id={self.id}, title={self.title}, agency={self.agency_name})>"
