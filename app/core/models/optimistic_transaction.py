from sqlalchemy import Column, String, Boolean, Float, DateTime, JSON
from app.db.base import Base

class OptimisticTransaction(Base):
    __tablename__ = "optimistic_transactions"
    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, index=True)
    asset_symbol = Column(String)
    quantity = Column(Float)
    side = Column(String)
    timestamp_initiated = Column(DateTime)
    expected_fee = Column(Float)
    expected_price = Column(Float)
    strategy_id = Column(String, nullable=True)
    user_initiated = Column(Boolean)
    status = Column(String) # pending | confirmed | replaced | failed
    provider_action_payload = Column(JSON)
