from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func

from app.infrastructure.db.models.base import Base


class PetFactModel(Base):
    """One durable fact the AI remembers about a dog. Soft-deleted by the owner."""

    __tablename__ = "pet_facts"

    id = Column(Integer, primary_key=True)
    pet_id = Column(Integer, ForeignKey("pets.id", ondelete="CASCADE"), nullable=False, index=True)
    fact = Column(Text, nullable=False)
    source = Column(String, nullable=False, default="ai")  # ai | user
    created_at = Column(DateTime, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)
