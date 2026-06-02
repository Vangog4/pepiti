from enum import Enum


class AgeCategory(str, Enum):
    PUPPY = "щенок (до 1 года)"
    YOUNG = "молодой (1–3 года)"
    ADULT = "взрослый (3–7 лет)"
    SENIOR = "пожилой (7+ лет)"


class SizeCategory(str, Enum):
    SMALL = "маленький (до 10 кг)"
    MEDIUM = "средний (10–25 кг)"
    LARGE = "крупный (25–45 кг)"
    GIANT = "гигант (45+ кг)"


class Sex(str, Enum):
    MALE = "кобель"
    FEMALE = "сука"


class EnergyLevel(str, Enum):
    LOW = "низкий"
    MEDIUM = "средний"
    HIGH = "высокий"


class TrainingLevel(str, Enum):
    BEGINNER = "1"
    BASIC = "2"
    INTERMEDIATE = "3"
    ADVANCED = "4"
    EXPERT = "5"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class ReminderType(str, Enum):
    DAILY_TRAINING = "daily_training"
    WEEKLY_REPORT = "weekly_report"
    REENGAGEMENT = "reengagement"
    PLAN_REMINDER = "plan_reminder"


class TaskDifficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"
