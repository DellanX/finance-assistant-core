from sqlalchemy import Column, String, Float, JSON
from app.db.base import Base

class Tranche(Base):
    __tablename__ = "tranches"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    tags = Column(JSON)
    cost_basis = Column(Float)
    history = Column(JSON) # versioned
