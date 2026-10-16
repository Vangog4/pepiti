#!/usr/bin/env python3
"""QA user-journey smoke — run inside bot container.

  podman exec pepito-bot_bot_1 python /app/scripts/qa_user_journey.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import traceback
from collections import Counter
from types import SimpleNamespace

results: list[tuple[str, str, str]] = []


def ok(name: str, detail: str = "") -> None:
    results.append(("PASS", name, detail))
    print(f"[PASS] {name}" + (f" — {detail}" if detail else ""), flush=True)


def fail(name: str, detail: str = "") -> None:
    results.append(("FAIL", name, detail))
    print(f"[FAIL] {name}" + (f" — {detail}" if detail else ""), flush=True)


def warn(name: str, detail: str = "") -> None:
    results.append(("WARN", name, detail))
    print(f"[WARN] {name}" + (f" — {detail}" if detail else ""), flush=True)


async def main() -> int:
    from app.core.config import settings

    ok("config", f"env={settings.APP_ENV}")

    # ── logic layer ──────────────────────────────────────────────────────────
    from app.logic.cascade import ModelCascade
    from app.logic.rules import contains_forbidden, rule

    c = ModelCascade()
    ok("logic cascade", f"{c.default} → {c.escalate}")
    assert rule("ai.free_daily_limit") == 5
    assert contains_forbidden("ветеринарный диагноз")
    ok("logic rules")

    # ── DB ───────────────────────────────────────────────────────────────────
    from sqlalchemy import func, select, text

    from app.infrastructure.db.engine import create_db_engine
    from app.infrastructure.db.models.pet import PetModel
    from app.infrastructure.db.models.user import UserModel
    from app.infrastructure.db.session import create_session_factory

    engine = create_db_engine()
    sf = create_session_factory(engine)
    async with sf() as s:
        users = (await s.execute(select(func.count()).select_from(UserModel))).scalar()
        pets = (await s.execute(select(func.count()).select_from(PetModel))).scalar()
        tables = set(
            (
                await s.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public'"))
            ).scalars()
        )
    ok("DB counts", f"users={users} pets={pets}")
    need = {"users", "pets", "training_plans", "training_tasks", "subscriptions", "coach_threads"}
    missing = need - tables
    if missing:
        fail("DB tables", str(missing))
    else:
        ok("DB tables", ", ".join(sorted(need)))

    # ── Redis rate limit + metrics ───────────────────────────────────────────
    from app.infrastructure.redis.ai_rate_limit import FREE_DAILY_LIMIT, AiRateLimiter
    from app.infrastructure.redis.metrics import BotMetrics

    rl = AiRateLimiter(settings.REDIS_URL)
    metrics = BotMetrics(settings.REDIS_URL)
    tid = 999001001
    await rl.reset(tid)
    for _ in range(FREE_DAILY_LIMIT):
        await rl.increment(tid)
    if await rl.is_allowed(tid):
        fail("rate_limit", f"still allowed after {FREE_DAILY_LIMIT}")
    else:
        ok("rate_limit free cap", f"blocked after {FREE_DAILY_LIMIT}")
    await rl.reset(tid)
    ok("metrics", json.dumps(await metrics.get_ai_stats()))

    # ── i18n ─────────────────────────────────────────────────────────────────
    from app.i18n import t

    for lang in ("ru", "en", "de", "fr", "es", "pt"):
        body = t("premium.upsell.body", lang, price=299)
        if "299" not in body:
            warn(f"i18n premium {lang}", f"no price: {body[:80]!r}")
        else:
            ok(f"i18n premium {lang}")

    # ── shop recommendations ─────────────────────────────────────────────────
    from app.core.shop_recommendations import AFTER_COMPLETION, AFTER_EXERCISE, get_shop_button

    puppy = SimpleNamespace(
        name="Балу", age_category="Щенок (4–12 мес)", size_category="Средний (10–25 кг)"
    )
    adult = SimpleNamespace(
        name="Рекс", age_category="Взрослый (3–7 лет)", size_category="Крупный (25–45 кг)"
    )
    b1 = get_shop_button(puppy, True, AFTER_EXERCISE)
    b2 = get_shop_button(adult, False, AFTER_COMPLETION)
    ok("shop puppy", b1.text)
    ok("shop completion", f"{b2.text} | {b2.url[:50]}")

    # ── DI ───────────────────────────────────────────────────────────────────
    from app.core.container import AppContainer

    cont = AppContainer()
    ai = cont.ai_service()
    if ai._metrics is None:
        fail("DI metrics", "not wired")
    else:
        ok("DI AiService+metrics")

    # ── Real Gemini user journey ─────────────────────────────────────────────
    print("… Gemini extract_profile", flush=True)
    profile = await ai.extract_pet_profile(
        language_code="ru",
        text="Собака Чарли бигль 2 года, тянет поводок на прогулке",
    )
    ok(
        "AI profile",
        json.dumps(
            {k: profile.get(k) for k in ("name", "breed", "age_category", "missing_fields")},
            ensure_ascii=False,
        ),
    )

    pet = PetModel(
        name=profile.get("name") or "Чарли",
        breed=profile.get("breed") or "Бигль",
        age_category=profile.get("age_category") or "Молодой (1–3 года)",
        size_category=profile.get("size_category") or "Средний (10–25 кг)",
        goal=profile.get("goal") or "Не тянуть поводок",
        behavior_issues=profile.get("behavior_issues") or "тянет поводок",
        training_level="3",
    )

    print("… Gemini training_plan", flush=True)
    plan = await ai.generate_training_plan(pet, lang="ru")
    fb = plan.get("title") in ("Базовая тренировка", "Basic training")
    if not plan.get("tasks"):
        fail("AI plan", "no tasks")
    else:
        ok("AI plan", f"fallback={fb} title={plan.get('title')!r} n={len(plan['tasks'])}")
        for i, tsk in enumerate(plan["tasks"][:3], 1):
            print(f"   · {i}. {tsk.get('title')} [{tsk.get('difficulty')}/{tsk.get('duration_minutes')}m]")

    print("… Gemini coach RU", flush=True)
    ans = await ai.answer_coach_question(
        pet, f"Хозяин: {pet.name} тянет поводок. Что делать?", lang="ru"
    )
    if ans.startswith("⚠️"):
        fail("AI coach RU", ans[:180])
    else:
        issues = []
        if "**" in ans:
            issues.append("markdown**")
        if contains_forbidden(ans):
            issues.append(f"forbidden:{contains_forbidden(ans)}")
        if not any(x in ans for x in ("🎯", "🛠", "<b>")):
            issues.append("weak_structure")
        if issues:
            warn("AI coach RU quality", f"{issues} len={len(ans)}")
        else:
            ok("AI coach RU", f"len={len(ans)}")
        print("   SAMPLE:\n" + ans[:450] + "\n   ---", flush=True)

    print("… Gemini intent", flush=True)
    titles = [t["title"] for t in plan.get("tasks", [])]
    intent = await ai.detect_training_intent(
        pet,
        titles,
        "ru",
        text=f"Выполнили {titles[0] if titles else 'сидеть'}, получилось!",
    )
    ok("AI intent", f"action={intent.get('action')} hint={intent.get('task_hint')!r}")

    print("… Gemini week_plan", flush=True)
    week = await ai.generate_week_plan(pet, lang="ru")
    ndays = len(week.get("days") or [])
    if ndays != 7:
        warn("AI week", f"days={ndays} title={week.get('title')!r}")
    else:
        ok("AI week", f"7 days title={week.get('title')!r}")

    if plan.get("tasks"):
        print("… Gemini explain", flush=True)
        t0 = plan["tasks"][0]
        exp = await ai.explain_exercise(t0["title"], t0["description"], lang="ru")
        if exp.startswith("⚠️"):
            fail("AI explain", exp[:120])
        else:
            ok("AI explain", f"len={len(exp)}")

    print("… Gemini progress", flush=True)
    prog = await ai.summarize_progress(pet, training_days=5, lang="ru")
    if prog.startswith("⚠️"):
        fail("AI progress", prog[:120])
    else:
        ok("AI progress", f"len={len(prog)}")

    print("… Gemini coach EN", flush=True)
    ans_en = await ai.answer_coach_question(pet, "Owner: dog pulls on leash badly", lang="en")
    cyr = sum(1 for ch in ans_en if ("а" <= ch.lower() <= "я") or ch.lower() == "ё")
    if ans_en.startswith("⚠️"):
        fail("AI coach EN", ans_en[:120])
    elif cyr > 40:
        warn("AI coach EN language", f"cyrillic_chars={cyr} sample={ans_en[:90]!r}")
    else:
        ok("AI coach EN", f"len={len(ans_en)} cyr={cyr}")

    print("… Gemini partial onboarding", flush=True)
    partial = await ai.extract_pet_profile(language_code="ru", text="У меня лабрадор")
    mf = partial.get("missing_fields") or []
    if "name" in mf or partial.get("clarify_question"):
        ok("AI partial onboarding", f"missing={mf} q={str(partial.get('clarify_question'))[:60]!r}")
    else:
        warn("AI partial", f"expected missing name, got keys={list(partial.keys())} mf={mf}")

    # postprocess XSS
    from app.services.ai_service import AiService as AIS

    dirty = "<strong>ok</strong><script>alert(1)</script>"
    clean = AIS._postprocess(dirty)
    if "<script>" in clean or "<strong>" in clean:
        fail("HTML sanitize", clean)
    else:
        ok("HTML sanitize", clean)

    # PDF
    try:
        from app.services.pdf_service import generate_training_pdf

        pdf_bytes = generate_training_pdf(
            "Чарли",
            "План QA",
            "Цель",
            [{"day": 1, "tasks": plan.get("tasks") or []}],
        )
        if pdf_bytes[:4] != b"%PDF":
            fail("PDF", repr(pdf_bytes[:20]))
        else:
            ok("PDF", f"{len(pdf_bytes)} bytes")
    except Exception as e:
        # try discover API
        import app.services.pdf_service as ps

        fail("PDF", f"{e}; exports={[x for x in dir(ps) if not x.startswith('_')]}")

    # coach free vs premium window
    from app.services.coach_service import CoachService

    msgs = []
    for i in range(25):
        msgs.append({"role": "user", "content": f"q{i}", "ts": i})
        msgs.append({"role": "coach", "content": f"a{i}", "ts": i})
    thread = SimpleNamespace(
        messages_json=msgs, summary="резюме длинного диалога", message_count=20, title=None
    )
    cs = CoachService(repo=None)  # type: ignore[arg-type]
    free_ctx = cs.build_prompt_context(thread, is_premium=False, lang="ru")
    prem_ctx = cs.build_prompt_context(thread, is_premium=True, lang="ru")
    ok("coach windows", f"free={len(free_ctx)} prem={len(prem_ctx)}")
    if "резюме" not in free_ctx:
        warn("coach summary", "summary missing when history truncated")
    else:
        ok("coach summary injected")

    # final metrics after AI calls
    final_ai = await metrics.get_ai_stats()
    ok("metrics after AI", json.dumps(final_ai))

    print("\n======== SUMMARY ========", flush=True)
    print(dict(Counter(s for s, _, _ in results)), flush=True)
    for st, name, detail in results:
        if st != "PASS":
            print(f"  {st}: {name} — {detail[:300]}", flush=True)

    return 1 if any(s == "FAIL" for s, _, _ in results) else 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except Exception:
        traceback.print_exc()
        raise SystemExit(2)
