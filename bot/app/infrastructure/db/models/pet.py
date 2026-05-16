from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.models.base import Base

class PetModel(Base):
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    breed = Column(String, nullable=True)
    sex = Column(String, nullable=True)
    age_category = Column(String, nullable=True)
    age_months = Column(Integer, nullable=True)
    size_category = Column(String, nullable=True)
    weight_kg = Column(Float, nullable=True)
    training_level = Column(String, nullable=True)
    temperament = Column(String, nullable=True)
    behavior_issues = Column(Text, nullable=True)
    goal = Column(Text, nullable=True)
    energy_level = Column(String, nullable=True)
    health_notes = Column(Text, nullable=True)
    training_schedule = Column(String, nullable=True)
    training_days = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("UserModel", back_populates="pets")
    training_plans = relationship("TrainingPlanModel", back_populates="pet", lazy="select")
    ai_conversations = relationship("AiConversationModel", back_populates="pet", lazy="select")
