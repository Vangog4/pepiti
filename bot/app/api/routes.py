import asyncio
import re
import time
from datetime import date, timedelta
from datetime import datetime as _dt
from pathlib import Path

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiohttp import web
from sqlalchemy import distinct, func, or_, select, text

from app.api.auth import validate_init_data
from app.api.mobile_auth import decode_jwt, issue_jwt, verify_vk_token
from app.core.config import settings
from app.core.shop import SHOP_URL_BY_SIZE, SHOP_URL_LONGPLAY, SHOP_URL_MAIN, SHOP_URL_TRAINING
from app.i18n import normalize_locale, t
from app.infrastructure.db.models.coach_thread import CoachThreadModel
from app.infrastructure.db.models.mobile_auth import MobileAuthModel
from app.infrastructure.db.models.pet import PetModel
from app.infrastructure.db.models.subscription import SubscriptionModel
from app.infrastructure.db.models.training import TrainingPlanModel, TrainingTaskModel
from app.infrastructure.db.models.user import UserModel
from app.infrastructure.db.repositories.training_repo import TrainingPlanRepository
from app.infrastructure.redis.admin_log import AdminLog
from app.infrastructure.redis.metrics import BotMetrics
from app.services.broadcast_service import run_broadcast
from app.services.referral_service import (
    REFERRAL_BONUS_DAYS,
    REFERRAL_MILESTONES,
    milestone_label,
    milestone_reward,
)
from app.services.training_service import TrainingService, tasks_for_today

_VALID_THREAD_STATUSES = {"active", "archived", "all"}

routes = web.RouteTableDef()

_WEBAPP_DIR = Path(__file__).parent.parent / "webapp"

# ── Validation constants ───────────────────────────────────────────────────────
_VALID_TRAINING_LEVELS = {"1", "2", "3", "4", "5"}
_VALID_AGE_CATEGORIES = {
    "Щенок (до 4 мес)",
    "Щенок (4–12 мес)",
    "Молодой (1–3 года)",
    "Взрослый (3–7 лет)",
    "Пожилой (7+ лет)",
}
_VALID_TIMEZONES = {
    "UTC",
    "UTC-12",
    "UTC-11",
    "UTC-10",
    "UTC-9",
    "UTC-8",
    "UTC-7",
    "UTC-6",
    "UTC-5",
    "UTC-4",
    "UTC-3",
    "UTC-2",
    "UTC-1",
    "UTC+1",
    "UTC+2",
    "UTC+3",
    "UTC+4",
    "UTC+5",
    "UTC+6",
    "UTC+7",
    "UTC+8",
    "UTC+9",
    "UTC+10",
    "UTC+11",
    "UTC+12",
    "UTC+13",
    "UTC+14",
}
_VALID_LANGS = {"ru", "en", "de", "fr", "es", "pt"}
_RE_TIME = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
_ALLOWED_EVENTS = {"share_click", "copy_click"}
_EVENT_KEY_MAP = {
    "share_click": BotMetrics.SHARE_CLICK,
    "copy_click": BotMetrics.COPY_CLICK,
}
_RE_CAMP_ID = re.compile(r"^[a-zA-Z0-9_-]{1,64}$")


def _auth(request: web.Request) -> int:
    """Return telegram_id from validated initData or raise HTTPUnauthorized."""
    raw = request.headers.get("X-Telegram-Init-Data", "")
    parsed = validate_init_data(raw, settings.BOT_TOKEN) if raw else None
    if not parsed:
        raise web.HTTPUnauthorized()
    tid = (parsed.get("user") or {}).get("id")
    if not tid:
        raise web.HTTPUnauthorized()
    return tid


def _auth_mobile(request: web.Request) -> int:
    """Return user_id (users.id PK) from JWT Bearer token or raise HTTPUnauthorized.

    Used exclusively for mobile (VK ID) endpoints.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise web.HTTPUnauthorized()
    token = auth_header[len("Bearer ") :]
    user_id = decode_jwt(token, settings.MOBILE_JWT_SECRET)
    if user_id is None:
        raise web.HTTPUnauthorized()
    return user_id


def _validate_pet(body: dict, lang: str = "ru") -> list:
    errors = []
    name = str(body.get("name", "")).strip()
    if not name:
        errors.append({"field": "name", "msg": t("webapp.validation.name_empty", lang)})
    elif len(name) > 30:
        errors.append({"field": "name", "msg": t("webapp.validation.name_long", lang)})

    if len(str(body.get("breed", "")).strip()) > 40:
        errors.append({"field": "breed", "msg": t("webapp.validation.breed_long", lang)})

    if len(str(body.get("goal", "")).strip()) > 150:
        errors.append({"field": "goal", "msg": t("webapp.validation.goal_long", lang)})

    level = str(body.get("training_level") or "").strip()
    if level and level not in _VALID_TRAINING_LEVELS:
        errors.append({"field": "training_level", "msg": t("webapp.validation.level", lang)})

    age = str(body.get("age_category") or "").strip()
    if age and age not in _VALID_AGE_CATEGORIES:
        errors.append({"field": "age_category", "msg": t("webapp.validation.age", lang)})

    return errors


def _validate_settings(body: dict, lang: str = "ru") -> list:
    errors = []
    rt = str(body.get("reminder_time") or "").strip()
    if rt and rt.lower() != "off" and not _RE_TIME.match(rt):
        errors.append({"field": "reminder_time", "msg": t("webapp.validation.reminder", lang)})

    tz = str(body.get("timezone") or "").strip()
    if tz and tz not in _VALID_TIMEZONES:
        errors.append({"field": "timezone", "msg": t("webapp.validation.timezone", lang)})

    loc = str(body.get("language_code") or "").strip()
    if loc and loc not in _VALID_LANGS:
        errors.append({"field": "language_code", "msg": t("webapp.validation.language", lang)})

    return errors


# ── Routes ─────────────────────────────────────────────────────────────────────


@routes.get("/")
async def index(request: web.Request) -> web.FileResponse:
    return web.FileResponse(_WEBAPP_DIR / "index.html")


@routes.get("/api/health")
async def health(request: web.Request) -> web.Response:
    """Public liveness. 200 if process+DB ok, 503 if DB is down."""
    payload: dict = {"ok": True, "service": "pepito-bot"}
    session_factory = request.app.get("session_factory")
    if session_factory is None:
        payload["ok"] = False
        payload["db"] = "missing"
        return web.json_response(payload, status=503)
    try:
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        payload["db"] = "ok"
    except Exception:
        payload["ok"] = False
        payload["db"] = "error"
        return web.json_response(payload, status=503)
    return web.json_response(payload)


@routes.get("/api/dashboard")
async def dashboard(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        if user is None:
            raise web.HTTPNotFound(reason="User not registered")

        pet_row = await session.execute(
            select(PetModel).where(PetModel.user_id == user.id).limit(1)
        )
        pet = pet_row.scalar_one_or_none()

        today_tasks = []
        plan_kind = None
        if pet:
            plan_repo = TrainingPlanRepository(session)
            plan = await plan_repo.get_active_plan(pet.id)
            if plan:
                plan_kind = "week" if plan.week_number is not None else "day"
                today_tasks = [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "duration_minutes": task.duration_minutes,
                        "difficulty": task.difficulty,
                        "is_completed": task.is_completed,
                        "day_of_week": task.day_of_week,
                    }
                    for task in tasks_for_today(plan)
                ]

        seven_days_ago = _dt.combine(date.today() - timedelta(days=6), _dt.min.time())
        chart_rows = await session.execute(
            select(
                func.date(TrainingTaskModel.completed_at).label("day"),
                func.count().label("cnt"),
            )
            .select_from(TrainingTaskModel)
            .join(TrainingPlanModel, TrainingTaskModel.plan_id == TrainingPlanModel.id)
            .where(
                TrainingPlanModel.user_id == user.id,
                TrainingTaskModel.is_completed == True,
                TrainingTaskModel.completed_at >= seven_days_ago,
            )
            .group_by(func.date(TrainingTaskModel.completed_at))
        )
        completed_by_day = {str(row.day): row.cnt for row in chart_rows.fetchall()}

        weekly_chart = [
            {
                "date": str(date.today() - timedelta(days=i)),
                "completed": completed_by_day.get(str(date.today() - timedelta(days=i)), 0),
            }
            for i in range(6, -1, -1)
        ]

        # Settings snapshot for the settings tab (loaded once with dashboard)
        reminder_raw = user.reminder_time or ""
        reminder_off = reminder_raw == "off"
        user_settings = {
            "reminder_time": "" if reminder_off else reminder_raw,
            "reminder_disabled": reminder_off,
            "timezone": user.timezone or "UTC",
            "language_code": user.language_code or "ru",
        }
        dashboard_lang = normalize_locale(user.language_code)

        # Growth data — referral count + achieved milestones
        ref_count_row = await session.execute(
            select(func.count())
            .select_from(UserModel)
            .where(
                UserModel.referrer_telegram_id == user.telegram_id,
                UserModel.referral_bonus_given == True,
            )
        )
        referral_count = ref_count_row.scalar() or 0

        milestone_rows = await session.execute(
            select(SubscriptionModel.plan_code).where(
                SubscriptionModel.user_id == user.id,
                SubscriptionModel.plan_code.like("milestone_%"),
            )
        )
        achieved_codes = {row[0] for row in milestone_rows.fetchall()}

    completed = sum(1 for t in today_tasks if t["is_completed"])
    is_admin = telegram_id in settings.ADMIN_TELEGRAM_IDS
    admin_stats = None
    if is_admin:
        async with session_factory() as adm_session:
            r_total = await adm_session.execute(select(func.count()).select_from(UserModel))
            r_premium = await adm_session.execute(
                select(func.count()).select_from(UserModel).where(UserModel.is_premium == True)
            )
            # referral_bonus_given is a business-logic anti-duplication flag, NOT analytics truth
            r_refs = await adm_session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(UserModel.referral_bonus_given == True)
            )
            today = date.today()
            r_new_today = await adm_session.execute(
                select(func.count())
                .select_from(UserModel)
                .where(func.date(UserModel.created_at) == today)
            )
            r_active_today = await adm_session.execute(
                select(func.count(func.distinct(TrainingPlanModel.user_id)))
                .select_from(TrainingTaskModel)
                .join(TrainingPlanModel, TrainingTaskModel.plan_id == TrainingPlanModel.id)
                .where(
                    TrainingTaskModel.is_completed == True,
                    func.date(TrainingTaskModel.completed_at) == today,
                )
            )
            onboarded_cnt = (
                await adm_session.execute(
                    select(func.count())
                    .select_from(UserModel)
                    .where(UserModel.onboarding_completed_at.isnot(None))
                )
            ).scalar() or 0
        premium_cnt = r_premium.scalar() or 0
        va = await request.app["metrics"].get_voice_stats()
        ai = await request.app["metrics"].get_ai_stats()
        admin_stats = {
            "total_users": r_total.scalar() or 0,
            "premium_users": premium_cnt,
            "referrals_given": r_refs.scalar() or 0,
            "new_today": r_new_today.scalar() or 0,
            "active_today": r_active_today.scalar() or 0,
            "conversion_pct": round(premium_cnt / onboarded_cnt * 100) if onboarded_cnt else 0,
            "va_mark_done": va["va_mark_done"],
            "va_premium_gate": va["va_premium_gate"],
            "va_fallback": va["va_fallback"],
            "ai_calls": ai["ai_calls"],
            "ai_schema_ok": ai["ai_schema_ok"],
            "ai_schema_fail": ai["ai_schema_fail"],
            "ai_escalate": ai["ai_escalate"],
            "ai_fallback": ai["ai_fallback"],
            "ai_forbidden": ai["ai_forbidden"],
            "schema_ok_rate_pct": ai["schema_ok_rate_pct"],
        }

    payload = {
        "user": {
            "telegram_id": user.telegram_id,
            "first_name": user.first_name,
            "is_premium": user.is_premium,
            "subscription_expires_at": (
                user.subscription_expires_at.isoformat() if user.subscription_expires_at else None
            ),
        },
        "pet": (
            {
                "name": pet.name,
                "breed": pet.breed,
                "training_level": pet.training_level,
                "goal": pet.goal,
                "energy_level": pet.energy_level,
                "age_category": pet.age_category,
            }
            if pet
            else None
        ),
        "today_tasks": today_tasks,
        "weekly_progress": {
            "total_tasks": len(today_tasks),
            "completed_tasks": completed,
            "training_days": pet.training_days if pet else 0,
            "weekly_chart": weekly_chart,
        },
        "settings": user_settings,
        "growth": {
            "referral_count": referral_count,
            "base_bonus_days": REFERRAL_BONUS_DAYS,
            "referral_link": (
                f"https://t.me/{settings.BOT_USERNAME}?start=ref_{user.telegram_id}"
                if settings.BOT_USERNAME
                else None
            ),
            "milestones": [
                {
                    "count": m["count"],
                    "bonus_days": m["bonus_days"],
                    "label": milestone_label(m, dashboard_lang),
                    "reward": milestone_reward(m, dashboard_lang),
                    "achieved": m["plan_code"] in achieved_codes,
                }
                for m in REFERRAL_MILESTONES
            ],
            "shop_urls": {
                "training": SHOP_URL_TRAINING,
                "longplay": SHOP_URL_LONGPLAY,
                "by_size": SHOP_URL_BY_SIZE,
                "main": SHOP_URL_MAIN,
            },
        },
        "meta": {
            "version": "1.5",
            "bot_username": settings.BOT_USERNAME or "",
            "plan_kind": plan_kind,
        },
        **({"is_admin": True, "admin_stats": admin_stats} if is_admin else {}),
    }

    return web.json_response(payload)


@routes.post("/api/tasks/{task_id}/toggle")
async def toggle_task(request: web.Request) -> web.Response:
    telegram_id = _auth(request)

    try:
        task_id = int(request.match_info["task_id"])
    except (ValueError, KeyError):
        raise web.HTTPBadRequest() from None

    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        task_row = await session.execute(
            select(TrainingTaskModel)
            .join(TrainingPlanModel, TrainingTaskModel.plan_id == TrainingPlanModel.id)
            .join(UserModel, TrainingPlanModel.user_id == UserModel.id)
            .where(
                TrainingTaskModel.id == task_id,
                UserModel.telegram_id == telegram_id,
            )
        )
        task = task_row.scalar_one_or_none()
        if task is None:
            raise web.HTTPNotFound()

        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        pet_row = await session.execute(
            select(PetModel).where(PetModel.user_id == user.id).limit(1)
        )
        pet = pet_row.scalar_one_or_none()
        if pet is None:
            raise web.HTTPNotFound()

        svc = TrainingService(TrainingPlanRepository(session), ai_service=None)  # type: ignore[arg-type]
        task, scope_done = await svc.toggle_task(task_id, pet)

        return web.json_response(
            {
                "id": task.id,
                "is_completed": task.is_completed,
                "plan_completed": scope_done,
                "training_days": pet.training_days or 0,
            }
        )


@routes.patch("/api/profile/pet")
async def update_pet(request: web.Request) -> web.Response:
    telegram_id = _auth(request)

    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        if user is None:
            raise web.HTTPNotFound()

        lang = normalize_locale(user.language_code)
        errors = _validate_pet(body, lang)
        if errors:
            return web.json_response({"errors": errors}, status=422)

        pet_row = await session.execute(
            select(PetModel).where(PetModel.user_id == user.id).limit(1)
        )
        pet = pet_row.scalar_one_or_none()
        if pet is None:
            raise web.HTTPNotFound(reason="Pet not found")

        for field in ("name", "breed", "goal", "training_level", "age_category"):
            if field in body:
                val = body[field]
                setattr(
                    pet,
                    field,
                    val.strip()
                    if isinstance(val, str) and val.strip()
                    else None
                    if not val
                    else val,
                )

        await session.commit()

        return web.json_response(
            {
                "ok": True,
                "pet": {
                    "name": pet.name,
                    "breed": pet.breed,
                    "training_level": pet.training_level,
                    "goal": pet.goal,
                    "age_category": pet.age_category,
                },
            }
        )


@routes.patch("/api/profile/settings")
async def update_settings(request: web.Request) -> web.Response:
    telegram_id = _auth(request)

    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        if user is None:
            raise web.HTTPNotFound()

        lang = normalize_locale(user.language_code)
        errors = _validate_settings(body, lang)
        if errors:
            return web.json_response({"errors": errors}, status=422)

        for field in ("reminder_time", "timezone", "language_code"):
            if field in body:
                raw = body[field]
                val = str(raw).strip() if raw else None
                if field == "reminder_time" and val and val.lower() == "off":
                    val = "off"
                elif field == "reminder_time" and not val:
                    val = None
                setattr(user, field, val)

        await session.commit()
        return web.json_response({"ok": True})


@routes.post("/api/broadcast")
async def broadcast(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    text = str(body.get("text") or "").strip()
    if not text:
        return web.json_response({"error": "Текст не может быть пустым"}, status=422)
    if len(text) > 4096:
        return web.json_response({"error": "Текст не более 4096 символов"}, status=422)

    button_text = str(body.get("button_text") or "").strip()
    button_url = str(body.get("button_url") or "").strip()
    camp_id = str(body.get("camp_id") or "").strip()

    if bool(button_text) != bool(button_url):
        return web.json_response(
            {"error": "button_text и button_url должны быть заданы вместе"}, status=422
        )
    if button_url and not (button_url.startswith("http://") or button_url.startswith("https://")):
        return web.json_response(
            {"error": "button_url должен начинаться с http:// или https://"}, status=422
        )
    if camp_id and not _RE_CAMP_ID.match(camp_id):
        camp_id = ""

    session_factory = request.app["session_factory"]
    bot = request.app["bot"]
    metrics = request.app["metrics"]

    target = str(body.get("target") or "all").strip()
    if target not in ("all", "premium", "free"):
        target = "all"

    async with session_factory() as session:
        q = select(UserModel.telegram_id).where(UserModel.onboarding_completed_at.isnot(None))
        if target == "premium":
            q = q.where(UserModel.is_premium == True)
        elif target == "free":
            q = q.where(UserModel.is_premium == False)
        result = await session.execute(q)
        ids = [row[0] for row in result.fetchall()]

    reply_markup = None
    if button_text and button_url:
        if not camp_id:
            camp_id = f"bc_{int(time.time())}"
        if settings.WEBAPP_PUBLIC_URL:
            tracked_url = f"{settings.WEBAPP_PUBLIC_URL.rstrip('/')}/api/go?camp={camp_id}"
            await metrics.create_campaign(camp_id, button_url, button_text, len(ids))
        else:
            tracked_url = button_url
        reply_markup = InlineKeyboardMarkup(
            inline_keyboard=[[InlineKeyboardButton(text=button_text, url=tracked_url)]]
        )

    alog: AdminLog | None = request.app.get("admin_log")
    if alog:
        asyncio.create_task(alog.log(telegram_id, "broadcast", target, f"queued={len(ids)}"))

    asyncio.create_task(run_broadcast(bot, ids, text, telegram_id, reply_markup=reply_markup))
    return web.json_response({"ok": True, "queued": len(ids), "target": target})


@routes.get("/api/admin/referral-stats")
async def admin_referral_stats(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        # referrals_started: users who arrived via a referral link
        # NOTE: referral_bonus_given is a business-logic dedup flag, NOT analytics truth.
        #       Use referrer_telegram_id IS NOT NULL for correct funnel counts.
        r_started = await session.execute(
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.referrer_telegram_id.isnot(None))
        )
        # referrals_completed: arrived via referral AND completed onboarding
        r_completed = await session.execute(
            select(func.count())
            .select_from(UserModel)
            .where(
                UserModel.referrer_telegram_id.isnot(None),
                UserModel.onboarding_completed_at.isnot(None),
            )
        )
        # unique referrers: distinct users who brought at least one completed referral
        r_unique = await session.execute(
            select(func.count(distinct(UserModel.referrer_telegram_id)))
            .select_from(UserModel)
            .where(
                UserModel.referrer_telegram_id.isnot(None),
                UserModel.onboarding_completed_at.isnot(None),
            )
        )
        # top 5 referrers ranked by completed referrals
        r_top = await session.execute(
            select(UserModel.referrer_telegram_id, func.count().label("cnt"))
            .where(
                UserModel.referrer_telegram_id.isnot(None),
                UserModel.onboarding_completed_at.isnot(None),
            )
            .group_by(UserModel.referrer_telegram_id)
            .order_by(func.count().desc())
            .limit(5)
        )
        # milestone breakdown: unique users who received each milestone tier
        r_ms = await session.execute(
            select(
                SubscriptionModel.plan_code,
                func.count(distinct(SubscriptionModel.user_id)).label("cnt"),
            )
            .where(SubscriptionModel.plan_code.like("milestone_%"))
            .group_by(SubscriptionModel.plan_code)
        )

    top_referrers = [{"telegram_id": row[0], "count": row[1]} for row in r_top.fetchall()]
    milestone_breakdown = {row[0]: row[1] for row in r_ms.fetchall()}

    return web.json_response(
        {
            "referrals_started": r_started.scalar() or 0,
            "referrals_completed": r_completed.scalar() or 0,
            "unique_referrers": r_unique.scalar() or 0,
            "top_referrers": top_referrers,
            "milestone_breakdown": milestone_breakdown,
        }
    )


@routes.post("/api/metrics/event")
async def track_event(request: web.Request) -> web.Response:
    _auth(request)
    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e
    event = body.get("event", "")
    if event not in _ALLOWED_EVENTS:
        raise web.HTTPUnprocessableEntity()
    await request.app["metrics"].inc(_EVENT_KEY_MAP[event])
    return web.json_response({"ok": True})


@routes.get("/api/admin/growth-stats")
async def admin_growth_stats(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()
    data = await request.app["metrics"].get_growth_counters()
    return web.json_response(data)


@routes.get("/api/go")
async def broadcast_redirect(request: web.Request) -> web.Response:
    camp_id = request.rel_url.query.get("camp", "").strip()
    if not camp_id:
        raise web.HTTPNotFound()
    url = await request.app["metrics"].track_click(camp_id)
    if url is None:
        raise web.HTTPNotFound()
    raise web.HTTPFound(url)


@routes.get("/api/admin/broadcast-stats")
async def admin_broadcast_stats(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()
    campaigns = await request.app["metrics"].get_all_campaigns()
    return web.json_response({"campaigns": campaigns})


# ── Admin user management ──────────────────────────────────────────────────


@routes.get("/api/admin/users")
async def admin_users(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    q = request.rel_url.query.get("q", "").strip()
    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        if q:
            if q.lstrip("-").isdigit():
                stmt = select(UserModel).where(UserModel.telegram_id == int(q)).limit(1)
            else:
                clean = q.lstrip("@")
                stmt = (
                    select(UserModel)
                    .where(
                        or_(
                            UserModel.username.ilike(f"%{clean}%"),
                            UserModel.first_name.ilike(f"%{clean}%"),
                        )
                    )
                    .limit(20)
                )
        else:
            stmt = select(UserModel).order_by(UserModel.created_at.desc()).limit(30)

        result = await session.execute(stmt)
        users = result.scalars().all()

    return web.json_response(
        {
            "users": [
                {
                    "telegram_id": u.telegram_id,
                    "username": u.username,
                    "first_name": u.first_name,
                    "is_premium": u.is_premium,
                    "subscription_expires_at": (
                        u.subscription_expires_at.strftime("%d.%m.%Y")
                        if u.subscription_expires_at
                        else None
                    ),
                    "onboarding_completed": u.onboarding_completed_at is not None,
                    "created_at": (u.created_at.strftime("%d.%m.%Y") if u.created_at else None),
                }
                for u in users
            ]
        }
    )


@routes.post("/api/admin/grant-premium")
async def admin_grant_premium(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    try:
        target_id = int(body.get("telegram_id", 0))
        days = int(body.get("days", 0))
    except (TypeError, ValueError):
        return web.json_response({"error": "Неверный формат"}, status=422)

    if days <= 0 or days > 3650:
        return web.json_response({"error": "days должен быть от 1 до 3650"}, status=422)

    session_factory = request.app["session_factory"]
    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == target_id)
        )
        user = user_row.scalar_one_or_none()
        if not user:
            return web.json_response({"error": "Пользователь не найден"}, status=404)

        from datetime import datetime as _dt2

        now = _dt2.utcnow()
        expires_at = max(user.subscription_expires_at or now, now) + timedelta(days=days)
        user.is_premium = True
        user.subscription_expires_at = expires_at
        session.add(
            SubscriptionModel(
                user_id=user.id,
                plan_code="admin_grant",
                status="active",
                provider="admin",
                expires_at=expires_at,
            )
        )
        await session.commit()
        name = user.first_name or user.username or str(target_id)

    alog: AdminLog | None = request.app.get("admin_log")
    if alog:
        await alog.log(
            telegram_id,
            "grant_premium_webapp",
            str(target_id),
            f"+{days} days, until {expires_at.strftime('%d.%m.%Y')}",
        )

    return web.json_response(
        {
            "ok": True,
            "name": name,
            "expires_at": expires_at.strftime("%d.%m.%Y"),
        }
    )


@routes.post("/api/admin/revoke-premium")
async def admin_revoke_premium(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    try:
        body = await request.json()
        target_id = int(body.get("telegram_id", 0))
    except Exception as e:
        raise web.HTTPBadRequest() from e

    session_factory = request.app["session_factory"]
    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == target_id)
        )
        user = user_row.scalar_one_or_none()
        if not user:
            return web.json_response({"error": "Пользователь не найден"}, status=404)
        user.is_premium = False
        user.subscription_expires_at = None
        await session.commit()
        name = user.first_name or user.username or str(target_id)

    alog: AdminLog | None = request.app.get("admin_log")
    if alog:
        await alog.log(telegram_id, "revoke_premium", str(target_id))

    return web.json_response({"ok": True, "name": name})


@routes.post("/api/admin/send-message")
async def admin_send_message(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    try:
        body = await request.json()
        target_id = int(body.get("telegram_id", 0))
        text = str(body.get("text", "")).strip()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    if not text:
        return web.json_response({"error": "Текст не может быть пустым"}, status=422)
    if len(text) > 4096:
        return web.json_response({"error": "Текст не более 4096 символов"}, status=422)

    bot = request.app["bot"]
    try:
        await bot.send_message(chat_id=target_id, text=text, parse_mode="HTML")
    except Exception as e:
        return web.json_response({"error": str(e)}, status=502)

    alog: AdminLog | None = request.app.get("admin_log")
    if alog:
        await alog.log(telegram_id, "send_msg", str(target_id), text[:60])

    return web.json_response({"ok": True})


@routes.get("/api/admin/actions")
async def admin_actions(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    if telegram_id not in settings.ADMIN_TELEGRAM_IDS:
        raise web.HTTPForbidden()

    alog: AdminLog | None = request.app.get("admin_log")
    entries = await alog.get_recent(30) if alog else []
    return web.json_response({"actions": entries})


# ── Coach threads ───────────────────────────────────────────────────────────


@routes.get("/api/coach/threads")
async def list_coach_threads(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    status_filter = request.rel_url.query.get("status", "all").strip()
    if status_filter not in _VALID_THREAD_STATUSES:
        raise web.HTTPBadRequest(reason="status must be active, archived, or all")

    session_factory = request.app["session_factory"]
    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        if user is None:
            raise web.HTTPNotFound(reason="User not registered")

        q = select(CoachThreadModel).where(CoachThreadModel.user_id == user.id)
        if status_filter != "all":
            q = q.where(CoachThreadModel.status == status_filter)
        q = q.order_by(CoachThreadModel.updated_at.desc())

        result = await session.execute(q)
        threads = result.scalars().all()

        return web.json_response(
            [
                {
                    "id": th.id,
                    "title": th.title or None,
                    "status": th.status,
                    "message_count": th.message_count,
                    "summary": th.summary,
                    "created_at": th.created_at.isoformat() if th.created_at else None,
                    "updated_at": th.updated_at.isoformat() if th.updated_at else None,
                    "is_active": user.active_coach_thread_id == th.id,
                }
                for th in threads
            ]
        )


@routes.get("/api/training/pdf")
async def download_training_pdf(request: web.Request) -> web.Response:
    """Return a PDF of the user's active training plan for today."""
    telegram_id = _auth(request)
    session_factory = request.app["session_factory"]

    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        if user is None:
            raise web.HTTPNotFound(reason="User not registered")

        pet_row = await session.execute(
            select(PetModel).where(PetModel.user_id == user.id).limit(1)
        )
        pet = pet_row.scalar_one_or_none()
        if pet is None:
            raise web.HTTPNotFound(reason="Pet not found")

        plan_repo = TrainingPlanRepository(session)
        plan = await plan_repo.get_active_plan(pet.id)
        if plan is None:
            raise web.HTTPNotFound(reason="No active plan for today")

        source_tasks = tasks_for_today(plan)
        tasks_data = sorted(
            [
                {
                    "day_of_week": task.day_of_week,
                    "title": task.title,
                    "description": task.description,
                    "duration_minutes": task.duration_minutes,
                    "difficulty": task.difficulty,
                    "is_completed": task.is_completed,
                }
                for task in source_tasks
            ],
            key=lambda row: row["day_of_week"] or 0,
        )

    from app.services.pdf_service import generate_training_pdf

    lang = normalize_locale(user.language_code)
    pdf_bytes = generate_training_pdf(
        pet_name=pet.name or "Питомец",
        plan_title=plan.title or "План тренировок",
        plan_goal=plan.goal or "",
        tasks=tasks_data,
        lang=lang,
    )

    safe_name = (pet.name or "plan").replace(" ", "_")
    return web.Response(
        body=pdf_bytes,
        content_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="pepito_{safe_name}.pdf"'},
    )


@routes.patch("/api/coach/threads/{thread_id}/archive")
async def archive_coach_thread(request: web.Request) -> web.Response:
    telegram_id = _auth(request)
    try:
        thread_id = int(request.match_info["thread_id"])
    except (ValueError, KeyError):
        raise web.HTTPBadRequest(reason="Invalid thread_id") from None

    session_factory = request.app["session_factory"]
    async with session_factory() as session:
        user_row = await session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        user = user_row.scalar_one_or_none()
        if user is None:
            raise web.HTTPNotFound(reason="User not registered")

        thread_row = await session.execute(
            select(CoachThreadModel).where(
                CoachThreadModel.id == thread_id,
                CoachThreadModel.user_id == user.id,
            )
        )
        thread = thread_row.scalar_one_or_none()
        if thread is None:
            raise web.HTTPNotFound(reason="Thread not found")

        thread.status = "archived"
        if user.active_coach_thread_id == thread_id:
            user.active_coach_thread_id = None
        await session.commit()

    return web.json_response({"ok": True})


# ── Mobile (VK ID + JWT) endpoints ─────────────────────────────────────────


@routes.post("/api/auth/vk")
async def auth_vk(request: web.Request) -> web.Response:
    """Mobile-only: authenticate with VK ID, return JWT.

    Body: {"vk_access_token": str, "vk_user_id": int, "first_name": str (optional)}
    Response: {"token": str, "user_id": int, "is_new": bool, "onboarding_done": bool}
    """
    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    vk_access_token = str(body.get("vk_access_token") or "").strip()
    vk_user_id_raw = body.get("vk_user_id")
    if not vk_access_token or vk_user_id_raw is None:
        raise web.HTTPBadRequest(reason="vk_access_token and vk_user_id are required")

    try:
        vk_user_id = int(vk_user_id_raw)
    except (TypeError, ValueError):
        raise web.HTTPBadRequest(reason="vk_user_id must be an integer") from None

    first_name = str(body.get("first_name") or "").strip() or None

    valid = await verify_vk_token(vk_access_token, vk_user_id)
    if not valid:
        raise web.HTTPUnauthorized(reason="VK token verification failed")

    session_factory = request.app["session_factory"]
    async with session_factory() as session:
        # Look up existing MobileAuthModel by vk_id
        ma_row = await session.execute(
            select(MobileAuthModel).where(MobileAuthModel.vk_id == vk_user_id)
        )
        mobile_auth = ma_row.scalar_one_or_none()

        if mobile_auth is None:
            # New VK user — create UserModel with placeholder telegram_id
            placeholder_telegram_id = -vk_user_id
            new_user = UserModel(
                telegram_id=placeholder_telegram_id,
                first_name=first_name,
            )
            session.add(new_user)
            await session.flush()  # get new_user.id

            mobile_auth = MobileAuthModel(
                user_id=new_user.id,
                vk_id=vk_user_id,
            )
            session.add(mobile_auth)
            await session.commit()
            await session.refresh(new_user)

            user_id = new_user.id
            is_new = True
            onboarding_done = new_user.onboarding_completed_at is not None
        else:
            # Existing VK user
            user_row = await session.execute(
                select(UserModel).where(UserModel.id == mobile_auth.user_id)
            )
            user = user_row.scalar_one_or_none()
            if user is None:
                raise web.HTTPInternalServerError(reason="User record missing")

            user_id = user.id
            is_new = False
            onboarding_done = user.onboarding_completed_at is not None

    token = issue_jwt(user_id, settings.MOBILE_JWT_SECRET, settings.MOBILE_JWT_EXPIRE_DAYS)
    return web.json_response(
        {
            "token": token,
            "user_id": user_id,
            "is_new": is_new,
            "onboarding_done": onboarding_done,
        }
    )


@routes.post("/api/push/register")
async def push_register(request: web.Request) -> web.Response:
    """Mobile-only: save RuStore push token.

    Header: Authorization: Bearer <jwt>
    Body: {"push_token": str}
    Response: {"ok": true}
    """
    user_id = _auth_mobile(request)

    try:
        body = await request.json()
    except Exception as e:
        raise web.HTTPBadRequest() from e

    push_token = str(body.get("push_token") or "").strip()
    if not push_token:
        raise web.HTTPBadRequest(reason="push_token is required")

    session_factory = request.app["session_factory"]
    async with session_factory() as session:
        ma_row = await session.execute(
            select(MobileAuthModel).where(MobileAuthModel.user_id == user_id)
        )
        mobile_auth = ma_row.scalar_one_or_none()
        if mobile_auth is None:
            raise web.HTTPNotFound(reason="Mobile auth record not found")

        mobile_auth.push_token = push_token
        await session.commit()

    return web.json_response({"ok": True})
