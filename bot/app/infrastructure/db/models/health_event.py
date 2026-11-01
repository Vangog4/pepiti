from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String, Text, func

from app.infrastructure.db.models.base import Base


class HealthEventModel(Base):
    """One completed procedure + when the next one is due. Newest per kind = the schedule."""

    __tablename__ = "health_events"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    kind = Column(String, nullable=False)  # vaccine | ticks | worms
    done_at = Column(Date, nullable=False)
    next_due_at = Column(Date, nullable=False, index=True)
    note = Column(Text, nullable=True)
    last_notified_on = Column(Date, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
