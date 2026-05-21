from sqlalchemy import Column, String, JSON
from app.db.base import Base

class Account(Base):
    __tablename__ = "accounts"
    id = Column(String, primary_key=True, index=True)
    provider_id = Column(String, index=True)
    external_account_id = Column(String)
    nickname = Column(String)
    tags = Column(JSON)
