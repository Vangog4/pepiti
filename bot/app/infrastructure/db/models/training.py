from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, JSON, func
from sqlalchemy.orm import relationship
from app.infrastructure.db.models.base import Base

class TrainingPlanModel(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    title = Column(String, nullable=False)
    goal = Column(Text, nullable=True)
    week_number = Column(Integer, nullable=True)
    plan_json = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    pet = relationship("PetModel", back_populates="training_plans")
    tasks = relationship("TrainingTaskModel", back_populates="plan", lazy="select")


class TrainingTaskModel(Base):
    __tablename__ = "training_tasks"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=False)
    day_of_week = Column(Integer, nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    duration_minutes = Column(Integer, nullable=True)
    difficulty = Column(String, nullable=True)
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)

    plan = relationship("TrainingPlanModel", back_populates="tasks")
