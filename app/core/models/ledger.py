from sqlalchemy import Column, String
from app.db.base import Base


class Ledger(Base):
    __tablename__ = "ledgers"
    id = Column(String, primary_key=True, index=True)
    account_id = Column(String, index=True)
    name = Column(String)
    description = Column(String)
