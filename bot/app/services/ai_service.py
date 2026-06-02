import json
import re

from google import genai
from google.genai import types

from app.infrastructure.db.models.pet import PetModel

_MODEL = "gemini-2.5-flash-lite"

_HTML_RULE = (
    "IMPORTANT: use only Telegram HTML tags: "
    "<b>bold</b>, <i>italic</i>. "
    "No asterisks (**), underscores, or other Markdown symbols."
)

_LANG_NAMES: dict[str, str] = {
    "ru": "Russian (русский)",
    "en": "English",
    "de": "German (Deutsch)",
    "fr": "French (Français)",
    "es": "Spanish (Español)",
    "pt": "Portuguese (Português)",
}


def _lang_instruction(lang: str) -> str:
    name = _LANG_NAMES.get(lang, "Russian (русский)")
    return f"\n\nIMPORTANT: Respond strictly in {name}."


_FALLBACK_PLAN_RU = {
    "title": "Базовая тренировка",
    "tasks": [
        {
            "title": "Контакт с хозяином",
            "description": "1. Встаньте перед питомцем.\n2. Скажите имя и дождитесь взгляда.\n3. Похвалите и угостите лакомством.\nПовторите 10 раз.",
            "duration_minutes": 5,
            "difficulty": "easy",
        },
        {
            "title": "Команда «Сидеть»",
            "description": "1. Держите лакомство над носом собаки.\n2. Плавно поднимите руку вверх и назад.\n3. Как только сядет — маркер «Да!» и лакомство.\nПовторите 10 раз.",
            "duration_minutes": 7,
            "difficulty": "easy",
        },
    ],
    "tip": "Тренируйтесь в тихом месте, короткими сессиями. Заканчивайте на успехе.",
}

_FALLBACK_PLAN_EN = {
    "title": "Basic training",
    "tasks": [
        {
            "title": "Name recall",
            "description": "1. Call the dog's name.\n2. Wait for eye contact.\n3. Reward immediately.\nRepeat 10 times.",
            "duration_minutes": 5,
            "difficulty": "easy",
        },
        {
            "title": "Sit command",
            "description": "1. Hold a treat above the dog's nose.\n2. Slowly move your hand up and back.\n3. Say 'Yes!' when they sit and reward.\nRepeat 10 times.",
            "duration_minutes": 7,
            "difficulty": "easy",
        },
    ],
    "tip": "Keep sessions short and practice in a quiet place. Always end on success.",
}

_FALLBACK_WEEK_PLAN_RU = {
    "title": "Базовый недельный план",
    "goal": "Общая дрессировка",
    "days": [
        {
            "day": i,
            "tasks": [
                {
                    "title": "Контакт с хозяином",
                    "description": "10 раз: позвать по имени, дождаться взгляда, похвалить лакомством.",
                    "duration_minutes": 5,
                    "difficulty": "easy",
                },
                {
                    "title": "Команда «Сидеть»",
                    "description": "10 раз: лакомство над носом, плавно вверх — пока не сядет, маркер «Да!» + угощение.",
                    "duration_minutes": 7,
                    "difficulty": "easy",
                },
            ],
        }
        for i in range(1, 8)
    ],
}

_FALLBACK_WEEK_PLAN_EN = {
    "title": "Basic weekly plan",
    "goal": "General training",
    "days": [
        {
            "day": i,
            "tasks": [
                {
                    "title": "Name recall",
                    "description": "10 reps: call by name, wait for eye contact, reward.",
                    "duration_minutes": 5,
                    "difficulty": "easy",
                },
                {
                    "title": "Sit command",
                    "description": "10 reps: treat above nose, move hand back slowly, say Yes! + reward when seated.",
                    "duration_minutes": 7,
                    "difficulty": "easy",
                },
            ],
        }
        for i in range(1, 8)
    ],
}


def _get_fallback_plan(lang: str) -> dict:
    return _FALLBACK_PLAN_RU if lang == "ru" else _FALLBACK_PLAN_EN


def _get_fallback_week_plan(lang: str) -> dict:
    return _FALLBACK_WEEK_PLAN_RU if lang == "ru" else _FALLBACK_WEEK_PLAN_EN


# Telegram HTML whitelist — only these tag names are allowed in parse_mode=HTML
_TG_ALLOWED_TAGS = frozenset({"b", "i", "u", "s", "code", "pre", "a"})


def _strip_unknown_tag(m: re.Match) -> str:
    """re.sub callback: keep whitelisted Telegram HTML tags, strip everything else."""
    name = re.match(r"</?(\w+)", m.group(0))
    return m.group(0) if (name and name.group(1).lower() in _TG_ALLOWED_TAGS) else ""


def _has_unclosed_tags(text: str) -> bool:
    """Return True if any whitelisted inline tag is left unclosed (would crash Telegram)."""
    stack: list[str] = []
    for m in re.finditer(r"<(/?)(\w+)[^>]*>", text):
        closing, tag = m.group(1), m.group(2).lower()
        if tag not in _TG_ALLOWED_TAGS:
            continue
        if closing:
            if stack and stack[-1] == tag:
                stack.pop()
        else:
            stack.append(tag)
    return bool(stack)


class AiService:
    def __init__(self, api_key: str):
        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=3,
                    initial_delay=1.0,
                    http_status_codes=[408, 429, 500, 502, 503, 504],
                ),
                timeout=30 * 1000,
            ),
        )

    async def generate_training_plan(self, pet: PetModel, lang: str = "ru") -> dict:
        breed = pet.breed or "порода неизвестна"
        age = pet.age_category or "возраст неизвестен"
        goal = pet.goal or "общая подготовка"
        level = pet.training_level or "3"
        issues = pet.behavior_issues or "нет"

        prompt = (
            f"Ты кинолог-тренер. Составь план тренировки на сегодня для собаки.\n\n"
            f"Питомец: {pet.name} ({breed}, {age}, уровень {level}/5).\n"
            f"Цель: {goal}. Проблемы: {issues}.\n\n"
            "Верни ТОЛЬКО валидный JSON (без markdown, без ```):\n"
            "{\n"
            '  "title": "короткое название плана (до 50 символов)",\n'
            '  "goal": "цель тренировки",\n'
            '  "tasks": [\n'
            "    {\n"
            '      "title": "название упражнения",\n'
            '      "description": "шаг 1\\nшаг 2\\nшаг 3",\n'
            '      "duration_minutes": 5,\n'
            '      "difficulty": "easy"\n'
            "    },\n"
            "    {\n"
            '      "title": "название второго упражнения",\n'
            '      "description": "шаг 1\\nшаг 2\\nшаг 3",\n'
            '      "duration_minutes": 8,\n'
            '      "difficulty": "medium"\n'
            "    }\n"
            "  ],\n"
            '  "tip": "один практичный совет владельцу"\n'
            "}\n\n"
            "difficulty: easy, medium или hard. Ровно 2 упражнения.\n"
            "В полях title и description используй только обычные буквы, цифры и знаки препинания. "
            "Никаких ■, •, ▮, ▸, ►, ─, ░ и подобных Unicode-символов рисования."
            + _lang_instruction(lang)
        )

        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text
            return self._parse_json(raw) or _get_fallback_plan(lang)
        except Exception:
            return _get_fallback_plan(lang)

    async def generate_week_plan(self, pet: PetModel, lang: str = "ru") -> dict:
        breed = pet.breed or "порода неизвестна"
        age = pet.age_category or "возраст неизвестен"
        goal = pet.goal or "общая подготовка"
        level = pet.training_level or "3"
        issues = pet.behavior_issues or "нет"

        prompt = (
            f"Ты кинолог-тренер. Составь план тренировок на 7 дней для собаки.\n\n"
            f"Питомец: {pet.name} ({breed}, {age}, уровень {level}/5).\n"
            f"Цель: {goal}. Проблемы: {issues}.\n\n"
            "Верни ТОЛЬКО валидный JSON (без markdown, без ```):\n"
            "{\n"
            '  "title": "короткое название плана (до 50 символов)",\n'
            '  "goal": "цель недели",\n'
            '  "days": [\n'
            "    {\n"
            '      "day": 1,\n'
            '      "tasks": [\n'
            '        {"title": "название", "description": "шаг 1\\nшаг 2\\nшаг 3", "duration_minutes": 5, "difficulty": "easy"},\n'
            '        {"title": "название", "description": "шаг 1\\nшаг 2\\nшаг 3", "duration_minutes": 8, "difficulty": "medium"}\n'
            "      ]\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            "Ровно 7 объектов в days (day: 1..7), ровно 2 задачи в каждом. difficulty: easy, medium или hard.\n"
            "В полях title и description используй только обычные буквы, цифры и знаки препинания. "
            "Никаких ■, •, ▮, ▸, ►, ─, ░ и подобных Unicode-символов рисования."
            + _lang_instruction(lang)
        )

        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text
            data = self._parse_week_json(raw)
            return data if data else _get_fallback_week_plan(lang)
        except Exception:
            return _get_fallback_week_plan(lang)

    async def explain_exercise(self, title: str, description: str, lang: str = "ru") -> str:
        prompt = (
            f"You are a professional dog trainer. Explain the following exercise in detail.\n\n"
            f"Exercise: {title}\n"
            f"Short description: {description}\n\n"
            "Provide a detailed explanation:\n"
            "🎯 <b>Goal:</b> [1-2 sentences]\n\n"
            "📋 <b>Step-by-step technique:</b>\n"
            "1. [detailed step]\n"
            "2. [detailed step]\n"
            "3. [detailed step]\n\n"
            "💡 <b>Tips:</b> [1-2 practical tips]\n\n"
            "⚠️ <b>Common mistakes:</b> [1 main mistake]\n\n"
            + _HTML_RULE
            + "\nMax 900 characters."
            + _lang_instruction(lang)
        )
        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text or ""
            return self._postprocess(raw)
        except Exception as e:
            return f"⚠️ Explanation unavailable. Try again later.\n<i>{e}</i>"

    async def analyze_media_question(
        self,
        pet: PetModel,
        media_bytes: bytes,
        mime_type: str,
        caption: str | None,
        history: str,
        lang: str = "ru",
    ) -> str:
        breed = pet.breed or "unknown breed"
        age = pet.age_category or "unknown age"

        if "video" in mime_type:
            media_word = "video"
        elif "audio" in mime_type:
            media_word = "voice message"
        else:
            media_word = "photo"

        prompt = (
            f"You are a professional dog trainer. The owner sent a {media_word} of their dog.\n\n"
            f"Pet: {pet.name} ({breed}, {age})."
            + (f" Caption: {caption}" if caption else "")
            + ("\nConversation history:\n" + history + "\n" if history else "")
            + f"\nAnalyze the {media_word} and give specific training advice.\n\n"
            "🎯 <b>What I see:</b> [1-2 sentences about behavior/technique]\n"
            "✅ <b>Doing right:</b> [1 point]\n"
            "🛠 <b>To improve:</b>\n"
            "1. [specific step]\n"
            "2. [specific step]\n\n"
            + _HTML_RULE
            + "\nMax 900 characters. Do not give veterinary diagnoses."
            + _lang_instruction(lang)
        )

        contents = [
            types.Part.from_bytes(data=media_bytes, mime_type=mime_type),
            types.Part.from_text(prompt),
        ]
        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=contents)
            ).text or ""
            return self._postprocess(raw)
        except Exception as e:
            return f"⚠️ Media analysis unavailable. Try again.\n<i>{e}</i>"

    async def answer_coach_question(self, pet: PetModel, history: str, lang: str = "ru") -> str:
        breed = pet.breed or "unknown breed"
        age = pet.age_category or "unknown age"
        goal = pet.goal or "general training"

        prompt = (
            f"You are a professional dog behaviourist and trainer. Consulting about:\n"
            f"<b>{pet.name}</b> — {breed}, {age}. Owner's goal: {goal}.\n\n"
            f"CONVERSATION HISTORY:\n{history}\n\n"
            "Evaluate the last question. If clarification is needed — ask EXACTLY ONE short question.\n"
            "If you have enough information — answer strictly in this format:\n\n"
            "🎯 <b>Main cause:</b> [1 sentence]\n\n"
            "🛠 <b>What to do (3 steps):</b>\n"
            "1. [Step 1]\n"
            "2. [Step 2]\n"
            "3. [Step 3]\n\n"
            "🚫 <b>What NOT to do:</b> [1 mistake]\n\n"
            + _HTML_RULE
            + "\nMax 1200 characters."
            + _lang_instruction(lang)
        )
        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text or ""
            return self._postprocess(raw)
        except Exception as e:
            return f"⚠️ Trainer is busy. Try again later.\n<i>{e}</i>"

    async def summarize_progress(self, pet: PetModel, training_days: int, lang: str = "ru") -> str:
        breed = pet.breed or "unknown breed"
        age = pet.age_category or "unknown age"
        goal = pet.goal or "general training"
        issues = pet.behavior_issues or "none"
        level = pet.training_level or "3"

        prompt = (
            f"You are a dog trainer. Give a brief progress summary based on data.\n\n"
            f"Pet: {pet.name} ({breed}, {age}).\n"
            f"Goal: {goal}. Issues: {issues}. Level: {level}/5.\n"
            f"Completed training sessions: {training_days}.\n\n"
            "Write 3-4 sentences:\n"
            "1. Evaluate progress by number of sessions.\n"
            "2. Give a specific tip to reach the goal.\n"
            "3. One step for next week.\n\n"
            + _HTML_RULE
            + "\nMax 600 characters."
            + _lang_instruction(lang)
        )
        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text or ""
            return self._postprocess(raw)
        except Exception as e:
            return f"⚠️ Analysis unavailable. Try later.\n<i>{e}</i>"

    async def premium_deep_analysis(
        self, pet: PetModel, training_days: int, lang: str = "ru"
    ) -> str:
        breed = pet.breed or "unknown breed"
        age = pet.age_category or "unknown age"
        goal = pet.goal or "general training"
        issues = pet.behavior_issues or "none"
        level = pet.training_level or "3"
        schedule = pet.training_schedule or "not specified"
        health = pet.health_notes or "none"

        prompt = (
            f"You are an expert dog trainer. Conduct a detailed progress analysis.\n\n"
            f"Pet: {pet.name} ({breed}, {age}, {pet.size_category or ''}).\n"
            f"Goal: {goal}. Issues: {issues}. Level: {level}/5.\n"
            f"Schedule: {schedule}. Health: {health}.\n"
            f"Total training sessions completed: {training_days}.\n\n"
            "Structured report:\n\n"
            "🔍 <b>Current level analysis:</b> [2 sentences]\n\n"
            f"📈 <b>Progress dynamics:</b> [assessment based on {training_days} sessions]\n\n"
            "🎯 <b>Focus for next 2 weeks:</b>\n"
            "1. [Specific exercise]\n"
            "2. [Specific exercise]\n\n"
            "⚠️ <b>Risks and limitations:</b> [1 point considering breed/health]\n\n"
            "💡 <b>Expert tip:</b> [1 non-obvious advice]\n\n"
            + _HTML_RULE
            + "\nMax 1400 characters."
            + _lang_instruction(lang)
        )
        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text or ""
            return self._postprocess(raw)
        except Exception as e:
            return f"⚠️ Deep analysis unavailable. Try later.\n<i>{e}</i>"

    async def extract_pet_profile(
        self,
        language_code: str,
        text: str | None = None,
        audio_bytes: bytes | None = None,
        mime_type: str | None = None,
        partial: dict | None = None,
    ) -> dict:
        """Extract structured pet profile from free-form text or voice.

        Returns dict with keys: name, breed, age_category, size_category,
        behavior_issues, goal, missing_fields, clarify_question.
        missing_fields contains only names from [name, breed, age_category].
        clarify_question is in the user's language when missing_fields is non-empty.
        """
        lang_phrase = {
            "ru": "Russian (русский)",
            "en": "English",
            "de": "German (Deutsch)",
            "fr": "French (français)",
            "es": "Spanish (español)",
            "pt": "Portuguese (português)",
        }.get(language_code, "Russian (русский)")

        known_parts: list[str] = []
        if partial:
            for key in (
                "name",
                "breed",
                "age_category",
                "size_category",
                "behavior_issues",
                "goal",
            ):
                if partial.get(key):
                    known_parts.append(f"{key}: {partial[key]}")
        known_block = ", ".join(known_parts) if known_parts else "nothing"

        prompt = (
            "You are a dog trainer assistant. Extract pet information from the user's message.\n\n"
            f"Already known: {known_block}\n\n"
            "Return ONLY valid JSON (no markdown, no code fences):\n"
            "{\n"
            '  "name": "Max",\n'
            '  "breed": "Labrador",\n'
            '  "age_category": "Молодой (1–3 года)",\n'
            '  "size_category": "Крупный (25–45 кг)",\n'
            '  "behavior_issues": "Pulls on leash",\n'
            '  "goal": "Stop pulling on leash",\n'
            '  "missing_fields": [],\n'
            '  "clarify_question": null\n'
            "}\n\n"
            "STRICT RULES:\n"
            "• age_category must be EXACTLY one of: "
            '"Щенок (до 4 мес)", "Щенок (4–12 мес)", "Молодой (1–3 года)", '
            '"Взрослый (3–7 лет)", "Пожилой (7+ лет)" — or null\n'
            "• size_category must be EXACTLY one of: "
            '"Маленький (до 10 кг)", "Средний (10–25 кг)", "Крупный (25–45 кг)", '
            '"Гигант (45+ кг)" — infer from breed even if not mentioned\n'
            "• behavior_issues: copy word-for-word from user's message (important training context)\n"
            "• goal: derive from behavior_issues if not stated explicitly\n"
            "• missing_fields: list only field names from [name, breed, age_category] "
            "that are STILL unknown after combining 'Already known' with the current message\n"
            f"• clarify_question: if missing_fields is non-empty, write ONE warm, friendly question "
            f"in {lang_phrase} about the FIRST missing field, using the pet's name if known. "
            "If missing_fields is empty, set to null.\n"
            "• Return ONLY JSON — no explanations, no markdown\n\n"
        )

        if audio_bytes and mime_type:
            contents: object = [
                types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                types.Part.from_text(
                    prompt + "User sent a voice message — transcribe and extract."
                ),
            ]
        else:
            contents = prompt + f"User message: {text or ''}"

        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=contents)
            ).text or ""
            parsed = self._parse_profile_json(raw)
            if parsed is not None:
                return parsed
        except Exception:
            pass

        # Safe fallback — preserve any partial, flag all core fields as missing
        result: dict = dict(partial or {})
        already_known = {k for k in ("name", "breed", "age_category") if result.get(k)}
        result["missing_fields"] = [
            f for f in ("name", "breed", "age_category") if f not in already_known
        ]
        result["clarify_question"] = None
        return result

    async def detect_training_intent(
        self,
        pet: PetModel,
        task_titles: list[str],
        language_code: str,
        text: str | None,
        media_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> dict:
        """Detect if user reports task completion or asks a coaching question.

        Returns {"action": "mark_done", "task_hint": "...", "message": "..."}
             or {"action": "none", "message": "..."}
        """
        lang_name = {
            "ru": "русском",
            "en": "English",
            "de": "Deutsch",
            "fr": "français",
            "es": "español",
            "pt": "português",
        }.get(language_code, "русском")

        if task_titles:
            tasks_block = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(task_titles))
        else:
            tasks_block = "нет активного плана на сегодня"

        media_word = ""
        if mime_type:
            if "audio" in mime_type:
                media_word = "голосовое сообщение"
            elif "video" in mime_type:
                media_word = "видео"
            else:
                media_word = "фото"

        prompt = (
            f"Ты AI-кинолог. Владелец собаки {pet.name} прислал"
            + (f" {media_word}" if media_word else " сообщение")
            + f".\n\nЗадачи из сегодняшнего плана тренировки:\n{tasks_block}\n\n"
            "ИНСТРУКЦИЯ:\n"
            "• Если владелец СООБЩАЕТ О ВЫПОЛНЕНИИ одной из задач "
            "(«выучили», «сделали», «отработали», «прошли», «получилось», "
            "«сделал», «закончили», «справились», «выполнили») — ответь строго в JSON:\n"
            '{"action":"mark_done","task_hint":"<ключевое слово из названия задачи>",'
            '"message":"<1–2 подбадривающих предложения с именем питомца>"}\n\n'
            "• Если прислано фото питомца без явного отчёта о выполнении — похвали питомца:\n"
            '{"action":"none","message":"<2–3 предложения с похвалой и коротким советом>"}\n\n'
            "• Во всех остальных случаях (вопрос, наблюдение, просьба о совете) — ответь как кинолог:\n"
            '{"action":"none","message":"<ответ кинолога не длиннее 800 символов, '
            'только HTML-теги Telegram>"}\n\n'
            f"ВАЖНО: отвечай строго на языке: {lang_name}.\n"
            "Отвечай ТОЛЬКО JSON-объектом без ```json и без пояснений."
        )

        if media_bytes and mime_type:
            contents: object = [
                types.Part.from_bytes(data=media_bytes, mime_type=mime_type),
                types.Part.from_text(prompt),
            ]
        else:
            contents = prompt + (f"\n\nСообщение: {text}" if text else "")

        try:
            raw = (
                await self.client.aio.models.generate_content(model=_MODEL, contents=contents)
            ).text or ""
        except Exception:
            return {"action": "none", "message": "⚠️ Не удалось обработать. Попробуй ещё раз."}

        parsed = self._parse_intent_json(raw)
        if parsed:
            return parsed
        return {"action": "none", "message": raw[:800], "_is_fallback": True}

    @staticmethod
    def _parse_profile_json(text: str) -> dict | None:
        text = text.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "missing_fields" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict) and "missing_fields" in data:
                    return data
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    @staticmethod
    def _parse_intent_json(text: str) -> dict | None:
        text = text.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "action" in data and "message" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        match = re.search(r'\{[^{}]*"action"[^{}]*\}', text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict) and "action" in data and "message" in data:
                    return data
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    @staticmethod
    def _parse_week_json(text: str) -> dict | None:
        text = text.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "days" in data and len(data["days"]) == 7:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict) and "days" in data:
                    return data
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    @staticmethod
    def _parse_json(text: str) -> dict | None:
        text = text.strip()
        # strip markdown code fences if model added them anyway
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        try:
            data = json.loads(text)
            if isinstance(data, dict) and "tasks" in data:
                return data
        except (json.JSONDecodeError, ValueError):
            pass
        # try extracting first {...} block
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group())
                if isinstance(data, dict) and "tasks" in data:
                    return data
            except (json.JSONDecodeError, ValueError):
                pass
        return None

    @staticmethod
    def _postprocess(text: str) -> str:
        """Normalize AI text for Telegram HTML parse_mode. Safe operations only."""
        # 1. Normalize line endings, strip trailing whitespace per line
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = "\n".join(line.rstrip() for line in text.split("\n"))

        # 2. Collapse 3+ newlines → double newline
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Layer C-pre: escape bare < that is not the start of a tag — must run
        # before any tag-processing so "x < y" becomes "x &lt; y" and survives
        text = re.sub(r"<(?![a-zA-Z/!])", "&lt;", text)

        # Layer B-1: tag aliases → canonical Telegram HTML
        text = text.replace("<strong>", "<b>").replace("</strong>", "</b>")
        text = text.replace("<em>", "<i>").replace("</em>", "</i>")
        text = text.replace("<del>", "<s>").replace("</del>", "</s>")
        text = text.replace("<strike>", "<s>").replace("</strike>", "</s>")
        text = text.replace("<ins>", "<u>").replace("</ins>", "</u>")
        text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<h[1-6][^>]*>(.*?)</h[1-6]>", r"\1", text, flags=re.DOTALL | re.IGNORECASE)

        # Layer B-2: block/list tags → readable plain structure
        text = re.sub(r"<li[^>]*>", "\n• ", text, flags=re.IGNORECASE)
        text = re.sub(r"</li>", "", text, flags=re.IGNORECASE)
        text = re.sub(r"<(?:ul|ol|p|div)[^>]*>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"</(?:ul|ol|p|div)>", "\n", text, flags=re.IGNORECASE)
        text = re.sub(r"<hr[^>]*>", "\n", text, flags=re.IGNORECASE)

        # Layer B-3: strip any remaining unknown tags, keep their text content
        text = re.sub(r"<[^>]+>", _strip_unknown_tag, text)

        # Layer C: escape bare & not already part of a valid HTML entity
        text = re.sub(r"&(?!(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);)", "&amp;", text)

        # Collapse extra blank lines introduced by block-tag substitutions
        text = re.sub(r"\n{3,}", "\n\n", text)

        # 4. Paragraph injection: only when text is long, has no \n\n, and has list markers
        if len(text) > 300 and "\n\n" not in text:
            lines = text.split("\n")
            out: list[str] = []
            for i, line in enumerate(lines):
                stripped = line.lstrip()
                if i > 0 and re.match(r"^(\d+\.\s|[-•]\s)", stripped):
                    out.append("")
                out.append(line)
            text = "\n".join(out)

        # Layer D: if unclosed inline tags remain after sanitisation, strip all HTML
        if _has_unclosed_tags(text):
            text = re.sub(r"<[^>]+>", "", text)

        return text.strip()

    async def generate_thread_title(self, first_question: str) -> str:
        prompt = (
            "Придумай короткое название (3–5 слов) для консультации кинолога по вопросу:\n"
            f'"{first_question[:200]}"\n\n'
            "Верни ТОЛЬКО название, без кавычек, без пояснений."
        )
        try:
            return (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text.strip()[:60]
        except Exception:
            return ""

    async def refresh_thread_summary(
        self, messages: list[dict], existing_summary: str | None
    ) -> str:
        formatted = "\n".join(
            f"{'Хозяин' if m['role'] == 'user' else 'Кинолог'}: {m['content']}"
            for m in messages[-20:]
        )
        prev = f"Предыдущее резюме: {existing_summary}\n\n" if existing_summary else ""
        prompt = (
            "Ты кинолог. Составь краткое (3–4 предложения) оперативное резюме консультации.\n"
            "Включи: главную проблему, данные советы, прогресс, что предстоит.\n\n"
            f"{prev}Диалог:\n{formatted}\n\n"
            "Резюме (только текст, без заголовков):"
        )
        try:
            return (
                await self.client.aio.models.generate_content(model=_MODEL, contents=prompt)
            ).text.strip()[:800]
        except Exception:
            return existing_summary or ""
