from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, func

from app.infrastructure.db.models.base import Base


class ActivityLogModel(Base):
    """A finished training day (kind=task, one per local date) or a walk (kind=walk)."""

    __tablename__ = "activity_log"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String, nullable=False)  # task | walk
    local_date = Column(Date, nullable=False, index=True)
    duration_min = Column(Integer, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
