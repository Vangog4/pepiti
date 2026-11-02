from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, func

from app.infrastructure.db.models.base import Base


class WeightLogModel(Base):
    __tablename__ = "weight_log"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    weight_kg = Column(Float, nullable=False)
    local_date = Column(Date, nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now())
