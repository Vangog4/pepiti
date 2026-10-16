from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.models.base import Base


class MobileAuthModel(Base):
    __tablename__ = "mobile_auth"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    vk_id = Column(BigInteger, nullable=False, unique=True)
    push_token = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("UserModel")
