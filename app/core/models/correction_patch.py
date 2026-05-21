from sqlalchemy import Column, String, JSON, DateTime
from app.db.base import Base

class CorrectionPatch(Base):
    __tablename__ = "correction_patches"
    id = Column(String, primary_key=True, index=True)
    target_type = Column(String)
    target_id = Column(String)
    patch_json = Column(JSON)
    created_by = Column(String)
    created_at = Column(DateTime)
