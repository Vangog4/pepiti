from sqlalchemy import BigInteger, Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.infrastructure.db.models.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    language_code = Column(String, nullable=True)
    timezone = Column(String, nullable=True, default="UTC")
    is_premium = Column(Boolean, nullable=False, default=False)
    subscription_expires_at = Column(DateTime, nullable=True)
    onboarding_completed_at = Column(DateTime, nullable=True)
    current_stage = Column(String, nullable=True)
    training_days = Column(Integer, default=0)
    referrer_telegram_id = Column(BigInteger, nullable=True)
    referral_bonus_given = Column(Boolean, nullable=False, default=False)
    reminder_time = Column(
        String(5), nullable=True
    )  # "HH:MM" local time; None → uses DEFAULT_REMINDER_TIME
    active_coach_thread_id = Column(
        Integer,
        ForeignKey(
            "coach_threads.id",
            use_alter=True,
            name="fk_users_active_coach_thread",
            ondelete="SET NULL",
        ),
        nullable=True,
    )
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    pets = relationship("PetModel", back_populates="user", lazy="select")
