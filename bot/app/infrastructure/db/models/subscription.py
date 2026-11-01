from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, func, text

from app.infrastructure.db.models.base import Base


class SubscriptionModel(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    plan_code = Column(String, nullable=False, default="premium_1m")
    status = Column(String, nullable=False, default="active")  # active | expired | refunded
    provider = Column(String, nullable=False, default="telegram_stars")
    telegram_payment_charge_id = Column(String, nullable=True)
    starts_at = Column(DateTime, nullable=False, server_default=func.now())
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        Index(
            "uq_subscriptions_charge_id",
            "telegram_payment_charge_id",
            unique=True,
            postgresql_where=text("telegram_payment_charge_id IS NOT NULL"),
        ),
    )
