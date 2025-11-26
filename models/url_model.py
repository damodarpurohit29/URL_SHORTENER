from sqlalchemy import Column, Integer, String, Text, DateTime, func, Boolean
from db.session import Base

class Url(Base):
    __tablename__ = "urls"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(8), unique=True, index=True)
    target_url = Column(Text, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=True)
    visit_count = Column(Integer, nullable=False, default=0)
    last_accessed_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
