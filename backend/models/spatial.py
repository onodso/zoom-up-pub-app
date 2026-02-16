from sqlalchemy import Column, String, Float, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from database import Base

class Mesh(Base):
    __tablename__ = "meshes"

    code = Column(String, primary_key=True, index=True) # JIS X 0410 Mesh Code
    lat = Column(Float) # Center Lat
    lon = Column(Float) # Center Lon
    municipality_code = Column(String, ForeignKey("municipalities.code"), nullable=True, index=True)
    level = Column(Integer) # 3 or 4

class Company(Base):
    __tablename__ = "companies"

    corporate_number = Column(String, primary_key=True, index=True) # 13 digits
    name = Column(String, index=True)
    address = Column(String)
    
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)
    mesh_code = Column(String, ForeignKey("meshes.code"), nullable=True, index=True)
    
    # 認定情報 (Flag/Tags)
    cert_flags = Column(JSON, nullable=True) # e.g. {"dx_cert": true, "health_mgmt": true}
    
    # Relationships
    mesh = relationship("Mesh")

class Building(Base):
    __tablename__ = "buildings"
    
    id = Column(String, primary_key=True) # GML ID usually
    mesh_code = Column(String, ForeignKey("meshes.code"), index=True)
    
    height = Column(Float, nullable=True)
    structure = Column(String, nullable=True)
    year_built = Column(Integer, nullable=True)
    
    lat = Column(Float)
    lon = Column(Float)
    
    mesh = relationship("Mesh")
