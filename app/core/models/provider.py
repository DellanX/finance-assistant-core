from sqlalchemy import Column, String, JSON
from app.db.base import Base

class Provider(Base):
    __tablename__ = "providers"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    type = Column(String)
    config = Column(JSON)
    secrets_ref = Column(String)
