from sqlalchemy import Column, String, Float, DateTime, JSON
from app.db.base import Base

class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(String, primary_key=True, index=True)
    ledger_id = Column(String, index=True)
    timestamp = Column(DateTime)
    asset_symbol = Column(String)
    quantity = Column(Float)
    unit_price = Column(Float)
    fee = Column(Float)
    currency = Column(String)
    source = Column(String) # provider | user | inference
    provider_metadata = Column(JSON)
    inference_events = Column(JSON)
