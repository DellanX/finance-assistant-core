from sqlalchemy import Column, String, JSON, DateTime
from app.db.base import Base

class Snapshot(Base):
    __tablename__ = "snapshots"
    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime)
    type = Column(String) # portfolio | tranche
    target_id = Column(String)
    data = Column(JSON)
