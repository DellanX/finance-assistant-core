from sqlalchemy import Column, String, JSON
from app.db.base import Base

class Portfolio(Base):
    __tablename__ = "portfolios"
    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, nullable=True) # nullable for global
    name = Column(String)
    assets = Column(JSON) # array of {symbol, quantity, cost_basis}
    history = Column(JSON)
