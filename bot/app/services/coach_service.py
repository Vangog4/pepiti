import time

from sqlalchemy.orm.attributes import flag_modified

from app.i18n.core import t
from app.infrastructure.db.models.coach_thread import CoachThreadModel
from app.infrastructure.db.repositories.coach_thread_repo import CoachThreadRepository


class CoachService:
    CONTEXT_MESSAGES_FREE = 10     # 5 exchanges
    CONTEXT_MESSAGES_PREMIUM = 20  # 10 exchanges
    MAX_STORED_MESSAGES = 40       # 20 exchanges
    SUMMARY_EVERY = 10             # refresh summary every 10th exchange

    def __init__(self, repo: CoachThreadRepository):
        self.repo = repo

    def build_prompt_context(
        self, thread: CoachThreadModel, is_premium: bool, lang: str = "ru"
    ) -> str:
        """Return formatted history string for AI prompt (past exchanges only)."""
        messages = thread.messages_json or []
        limit = self.CONTEXT_MESSAGES_PREMIUM if is_premium else self.CONTEXT_MESSAGES_FREE
        recent = messages[-limit:] if len(messages) > limit else messages

        parts = []
        if thread.summary and len(messages) > limit:
            summary_header = t("coach.summary.header", lang)
            parts.append(f"{summary_header}\n{thread.summary}\n\n---")

        owner_label = t("coach.role.owner", lang)
        trainer_label = t("coach.role.trainer", lang)
        for msg in recent:
            role = owner_label if msg["role"] == "user" else trainer_label
            parts.append(f"{role}: {msg['content']}")

        return "\n".join(parts)

    def save_exchange(
        self, thread: CoachThreadModel, question: str, answer: str
    ) -> None:
        """Append exchange to thread messages (in-memory). Caller must commit session."""
        messages = list(thread.messages_json or [])
        ts = int(time.time())
        messages.append({"role": "user", "content": question[:1000], "ts": ts})
        messages.append({"role": "coach", "content": answer[:4000], "ts": ts})
        if len(messages) > self.MAX_STORED_MESSAGES:
            messages = messages[-self.MAX_STORED_MESSAGES:]
        thread.messages_json = messages
        thread.message_count = (thread.message_count or 0) + 1
        flag_modified(thread, "messages_json")

    def should_generate_title(self, thread: CoachThreadModel) -> bool:
        return thread.message_count == 1 and thread.title is None

    def should_refresh_summary(self, thread: CoachThreadModel) -> bool:
        mc = thread.message_count or 0
        return mc > 0 and mc % self.SUMMARY_EVERY == 0
