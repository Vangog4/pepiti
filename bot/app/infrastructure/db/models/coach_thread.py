from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text, func

from app.infrastructure.db.models.base import Base


class CoachThreadModel(Base):
    __tablename__ = "coach_threads"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(Text, nullable=True)
    status = Column(String(20), nullable=False, server_default="active", default="active")
    summary = Column(Text, nullable=True)
    message_count = Column(Integer, nullable=False, server_default="0", default=0)
    messages_json = Column(JSON, nullable=True, default=list)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
