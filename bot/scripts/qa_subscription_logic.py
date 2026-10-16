#!/usr/bin/env python3
"""Real-DB checks: subscription stacking, expire safety, rate limit, shop."""
from __future__ import annotations

import asyncio
import json
import sys
from collections import Counter
from datetime import datetime, timedelta
from types import SimpleNamespace

from sqlalchemy import func, select, text


async def main() -> int:
    from app.core.config import settings
    from app.core.shop_recommendations import (
        AFTER_COMPLETION,
        AFTER_EXERCISE,
        get_shop_button,
    )
    from app.infrastructure.db.engine import create_db_engine
    from app.infrastructure.db.models.pet import PetModel
    from app.infrastructure.db.models.subscription import SubscriptionModel
    from app.infrastructure.db.models.training import TrainingPlanModel
    from app.infrastructure.db.models.user import UserModel
    from app.infrastructure.db.repositories.subscription_repo import SubscriptionRepository
    from app.infrastructure.db.repositories.user_repo import UserRepository
    from app.infrastructure.db.session import create_session_factory
    from app.infrastructure.redis.ai_rate_limit import FREE_DAILY_LIMIT, AiRateLimiter
    from app.infrastructure.redis.metrics import BotMetrics
    from app.logic.rules import rule
    from app.scheduler.jobs.expire_subscriptions import expire_subscriptions
    from app.services.subscription_service import (
        PREMIUM_1M_STARS,
        PREMIUM_DURATION_DAYS,
        SubscriptionService,
    )

    results: list[tuple[str, str, str]] = []

    def ok(n: str, d: str = "") -> None:
        results.append(("PASS", n, d))
        print(f"[PASS] {n}" + (f" — {d}" if d else ""), flush=True)

    def fail(n: str, d: str = "") -> None:
        results.append(("FAIL", n, d))
        print(f"[FAIL] {n}" + (f" — {d}" if d else ""), flush=True)

    def warn(n: str, d: str = "") -> None:
        results.append(("WARN", n, d))
        print(f"[WARN] {n}" + (f" — {d}" if d else ""), flush=True)

    engine = create_db_engine()
    sf = create_session_factory(engine)

    async with sf() as s:
        users = (await s.execute(select(func.count()).select_from(UserModel))).scalar()
        pets = (await s.execute(select(func.count()).select_from(PetModel))).scalar()
        subs = (await s.execute(select(func.count()).select_from(SubscriptionModel))).scalar()
        plans = (await s.execute(select(func.count()).select_from(TrainingPlanModel))).scalar()
        ok("DB census", f"users={users} pets={pets} subs={subs} plans={plans}")

        orphans = (
            await s.execute(
                text(
                    "SELECT count(*) FROM pets p LEFT JOIN users u ON u.id=p.user_id WHERE u.id IS NULL"
                )
            )
        ).scalar()
        (fail if orphans else ok)("orphan pets", str(orphans) if orphans else "0")

        now = datetime.utcnow()
        stale = (
            await s.execute(
                select(UserModel).where(
                    UserModel.is_premium.is_(True),
                    UserModel.subscription_expires_at.is_not(None),
                    UserModel.subscription_expires_at <= now,
                )
            )
        ).scalars().all()
        if stale:
            warn("stale premium flags", f"{len(stale)} users (until cron)")
        else:
            ok("no stale premium flags")

    # Stacking + expire safety on synthetic user
    async with sf() as s:
        repo = SubscriptionRepository(s)
        urepo = UserRepository(s)
        svc = SubscriptionService(repo, urepo)
        tid = 999888777
        u = await urepo.get_by_telegram_id(tid)
        if not u:
            u = UserModel(
                telegram_id=tid, first_name="QA", language_code="ru", is_premium=False
            )
            s.add(u)
            await s.commit()
            await s.refresh(u)

        await s.execute(text("DELETE FROM subscriptions WHERE user_id=:uid"), {"uid": u.id})
        await s.commit()

        far = datetime.utcnow() + timedelta(days=40)
        await repo.create(
            user_id=u.id,
            expires_at=far,
            plan_code="referral_bonus",
            provider="referral",
            charge_id=None,
        )
        u.is_premium = True
        u.subscription_expires_at = far
        await s.commit()

        await svc.activate(user_id=u.id, telegram_id=tid, charge_id="qa_charge_stack_1")
        await s.refresh(u)
        days_left = (u.subscription_expires_at - datetime.utcnow()).total_seconds() / 86400
        if days_left > 65:
            ok("subscription stacking", f"days_left≈{days_left:.1f}")
        else:
            fail("subscription stacking", f"days_left≈{days_left:.1f}")

        await svc.activate(user_id=u.id, telegram_id=tid, charge_id="qa_charge_stack_1")
        cnt = (
            await s.execute(
                text(
                    "SELECT count(*) FROM subscriptions WHERE telegram_payment_charge_id='qa_charge_stack_1'"
                )
            )
        ).scalar()
        (ok if cnt == 1 else fail)("charge idempotent", f"rows={cnt}")

        past = datetime.utcnow() - timedelta(days=1)
        await s.execute(
            text(
                "INSERT INTO subscriptions (user_id, plan_code, status, provider, expires_at, starts_at, created_at) "
                "VALUES (:uid, 'old_ref', 'active', 'referral', :p, :p, :p)"
            ),
            {"uid": u.id, "p": past},
        )
        await s.commit()

    await expire_subscriptions(sf)

    async with sf() as s2:
        repo2 = SubscriptionRepository(s2)
        still = await repo2.get_active(u.id)
        u2 = await s2.get(UserModel, u.id)
        if still and u2 and u2.is_premium:
            ok("expire keeps stacked premium", f"expires={u2.subscription_expires_at}")
        else:
            fail(
                "expire keeps stacked premium",
                f"active={still} premium={getattr(u2, 'is_premium', None)}",
            )
        exp_cnt = (
            await s2.execute(
                text(
                    "SELECT count(*) FROM subscriptions WHERE user_id=:uid AND status='expired'"
                ),
                {"uid": u.id},
            )
        ).scalar()
        act_cnt = (
            await s2.execute(
                text(
                    "SELECT count(*) FROM subscriptions WHERE user_id=:uid AND status='active' AND expires_at>NOW()"
                ),
                {"uid": u.id},
            )
        ).scalar()
        ok("expire row counts", f"expired={exp_cnt} active_valid={act_cnt}")

        await s2.execute(text("DELETE FROM subscriptions WHERE user_id=:uid"), {"uid": u.id})
        await s2.execute(
            text(
                "UPDATE users SET is_premium=false, subscription_expires_at=NULL WHERE id=:uid"
            ),
            {"uid": u.id},
        )
        await s2.commit()
        ok("QA cleanup")

    rl = AiRateLimiter(settings.REDIS_URL)
    tid_rl = 888777666
    await rl.reset(tid_rl)
    for _ in range(FREE_DAILY_LIMIT):
        if not await rl.is_allowed(tid_rl):
            fail("rate limit mid", "blocked early")
            break
        await rl.increment(tid_rl)
    else:
        if not await rl.is_allowed(tid_rl):
            ok("rate limit hard block", f"limit={FREE_DAILY_LIMIT}")
        else:
            fail("rate limit", "still allowed")
    await rl.reset(tid_rl)

    puppy = SimpleNamespace(
        name="Балу", age_category="Щенок (4–12 мес)", size_category="Средний"
    )
    adult = SimpleNamespace(
        name="Рекс",
        age_category="Взрослый (3–7 лет)",
        size_category="Крупный (25–45 кг)",
    )
    b1 = get_shop_button(puppy, True, AFTER_EXERCISE)
    b2 = get_shop_button(adult, False, AFTER_COMPLETION)
    ok("shop buttons", f"{b1.text[:35]} | {b2.text[:35]}")

    assert rule("premium.stars_1m") == PREMIUM_1M_STARS == 299
    assert PREMIUM_DURATION_DAYS == 30
    ok("rules constants", f"stars={PREMIUM_1M_STARS}")

    ai = await BotMetrics(settings.REDIS_URL).get_ai_stats()
    ok("ai metrics", json.dumps(ai))

    print("\n======== SUMMARY ========", flush=True)
    print(dict(Counter(r[0] for r in results)), flush=True)
    for st, n, d in results:
        if st != "PASS":
            print(f"  {st}: {n} — {d}", flush=True)
    return 1 if any(r[0] == "FAIL" for r in results) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
