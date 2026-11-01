"""English (en) — full translation."""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Pepito — Dog Training AI</b>",
    "menu.main.choose": "Choose a section:",
    "menu.btn.training": "🏋️ Training",
    "menu.btn.week_plan": "📅 Week",
    "menu.btn.stats": "📊 Stats",
    "menu.btn.coach": "💬 Trainer",
    "menu.btn.profile": "🐶 Passport",
    "menu.btn.premium": "⭐ Premium",
    "menu.btn.premium.active": "⭐ Premium ✓",
    "menu.btn.shop": "🛒 Shop",
    "menu.btn.invite": "🎁 Friends",
    "menu.btn.webapp": "📱 App",
    "menu.main.streak": "{emoji} Trainings completed: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "day",
    "menu.main.streak.days.few": "days",
    "menu.main.streak.days.many": "days",
    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 Menu",
    "common.back.btn": "🔙 Back",
    "common.menu.btn": "🔙 Menu",
    # ── Errors / Guards ────────────────────────────────────────────────────────
    "error.no_pet": "Please complete registration first: /start",
    # ── Settings ───────────────────────────────────────────────────────────────
    "settings.main.title": "⚙️ <b>Settings</b>",
    "settings.main.reminder_on": "⏰ Reminders: <b>{time} ({tz})</b>",
    "settings.main.reminder_default": "⏰ Reminders: <b>10:00 ({tz})</b> (default)",
    "settings.main.reminder_off": "⏰ Reminders: <b>off</b>",
    "settings.language.title": "🌐 <b>Language</b>",
    "settings.language.choose": "Choose interface language:",
    "settings.language.saved": "✅ Language changed to <b>{name}</b>.",
    "settings.language.btn": "🌐 Language",
    "settings.btn": "⚙️ Settings",
    "settings.reminder.btn": "⏰ Reminders",
    # ── Onboarding (Stage 9: conversational AI) ────────────────────────────────
    "onboarding.start.returning": "Welcome back, {name}! 🐾\nWhat shall we do today?",
    "onboarding.ai.welcome": (
        "Hi, <b>{name}</b>! I'm Pepito — your AI dog trainer. 🐶\n\n"
        "Tell me about your dog: name, breed, age, and what challenges you're facing?\n\n"
        "<i>You can type or send a voice message.</i>\n\n"
        "<b>Example:</b> «Beagle Charlie, 2 years old, pulls on the leash and barks at other dogs»"
    ),
    "onboarding.ai.thinking": "⏳ <i>Analysing...</i>",
    "onboarding.ai.photo_prompt": (
        "📷 Cute pet! Tell me about them in text or voice:\n"
        "name, breed, age and what you need help with?"
    ),
    "onboarding.ai.clarify": "Got it — <b>{summary}</b>\n\n{question}",
    "onboarding.ai.clarify.name": "What's your pet's name?",
    "onboarding.ai.clarify.breed": "What breed is it?",
    "onboarding.ai.clarify.age_category": "How old is it? (puppy, young, or adult?)",
    "onboarding.done.welcome": (
        "🎉 <b>Profile created!</b>\n\nWelcome, {name}!\nI'm ready to help you train <b>{pet}</b>."
    ),
    "onboarding.done.referral_bonus": "\n\n🎁 <b>Referral bonus:</b> +{days} days Premium activated!",
    "onboarding.done.milestone": "\n🏆 <b>Referral milestone:</b> {label} — {reward}!",
    "onboarding.done.plan_loading": "🐾 <i>Building the first training plan for {pet}...</i>",
    "onboarding.done.first_plan": "🏋️ <b>Here's your first plan!</b>\n\n{plan}",
    "onboarding.done.fallback": "Choose where to start 👇",
    # ── Training ───────────────────────────────────────────────────────────────
    "training.loading": "🐾 <i>Building a plan for {name}...</i>",
    "training.refresh.confirm": "🔄 <b>Generate a new plan?</b>\n\nYour current progress will be reset.",
    "training.refresh.confirm.yes": "✅ Yes, new plan",
    "training.refresh.confirm.no": "❌ No",
    "training.refresh.loading": "🔄 <i>Generating a new plan for {name}...</i>",
    "training.refresh.toast": "Generating new plan…",
    "training.week.loading": "📅 <i>Building a weekly plan for {name}...</i>",
    "training.week.refresh.confirm": (
        "🔄 <b>Generate a new weekly plan?</b>\n\nYour current weekly progress will be reset."
    ),
    "training.week.refresh.loading": "🔄 <i>Generating a new weekly plan for {name}...</i>",
    "training.week.empty": (
        "📅 <b>Weekly plan</b>\n\n"
        "🌱 <b>No tasks yet</b>\n\n"
        "Start with the daily plan — Pepito will build the weekly plan "
        "once you have some progress!"
    ),
    "training.week.empty.cta.btn": "🏋️ Training",
    "training.explain.btn": "📖 Explain",
    "training.refresh.btn": "🔄 New plan",
    "training.explain.loading": "🔍 <i>Explaining exercise «{title}»...</i>",
    "training.explain.back_daily.btn": "🔙 Plan",
    "training.explain.back_weekly.btn": "🔙 Back to plan",
    "training.task.not_found": "Task not found.",
    "training.plan.not_found": "Plan not found.",
    "training.task.toggle.done": "✅ Done!",
    "training.task.toggle.undone": "↩️ Undone",
    "training.share.text": "{name} and I have trained {n} {days} in a row with Pepito! 🐾",
    "training.share.btn": "📤 Share",
    "training.done": ("\n\n🎉 <b>Training complete! Great work!</b>\n{emoji} Total trainings: {n}"),
    "training.week_done": (
        "\n\n🎉 <b>{day} complete! Great work!</b>\n{emoji} Total trainings: {n}"
    ),
    "training.stats.empty": (
        "🌱 <b>You're just getting started!</b>\n\n"
        "Your first session is the most important.\n"
        "Open today's plan and mark the first exercise done — "
        "your training count will start growing!"
    ),
    "training.stats.empty.cta": "🏋️ Start training",
    "training.minutes.abbr": "min",
    "training.goal.label": "Goal",
    "training.day.1": "Monday",
    "training.day.2": "Tuesday",
    "training.day.3": "Wednesday",
    "training.day.4": "Thursday",
    "training.day.5": "Friday",
    "training.day.6": "Saturday",
    "training.day.7": "Sunday",
    "training.day.short.1": "Mo",
    "training.day.short.2": "Tu",
    "training.day.short.3": "We",
    "training.day.short.4": "Th",
    "training.day.short.5": "Fr",
    "training.day.short.6": "Sa",
    "training.day.short.7": "Su",
    "coach.display.photo": "[📷 Photo]",
    "coach.display.voice": "[🎤 Voice]",
    "coach.display.video": "[🎥 Video]",
    "defaults.pet_name": "Pet",
    # ── AI / Coach ─────────────────────────────────────────────────────────────
    "ai.fallback": (
        "🧠 <b>The trainer is handling too many requests right now</b>\n\n"
        "Try again in a moment — this usually resolves quickly.\n"
        "<i>If the issue persists, type /menu and try again.</i>"
    ),
    "ai.rate_limit": (
        "💬 <b>Daily limit reached</b>\n\n"
        "Free plan: <b>{limit} AI requests per day</b>\n"
        "Limit resets at your local midnight.\n\n"
        "⭐ <b>Premium — unlimited:</b>\n"
        "💬 Unlimited trainer questions\n"
        "🧠 In-depth progress analysis\n"
        "🎁 Personalised recommendations"
    ),
    "ai.rate_limit.btn": "⭐ Premium",
    "ai.analyzing.premium": "🧠 <i>Running in-depth analysis...</i>",
    "ai.analyzing.free": "🧠 <i>Analysing progress...</i>",
    "ai.progress.premium.header": "⭐ <b>In-depth analysis for {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Progress analysis for {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 Stats",
    "ai.retry.btn": "🔄 Retry",
    "ai.back_menu.btn": "🔙 Menu",
    "coach.entry": (
        "💬 <b>Ask the trainer</b>\n\n"
        "Ask anything about training or your pet's behaviour — or send a <b>📷 photo</b>.\n"
        "<i>E.g.: «How do I stop pulling on the leash?» or «Why does my dog ignore “Down”?»</i>\n\n"
        "Free: text + photo\n"
        "⭐ Premium: + 🎤 voice messages and 🎥 videos"
    ),
    "coach.thinking": "🧠 <i>Analysing your question...</i>",
    "coach.media.thinking": "🔍 <i>Analysing media...</i>",
    "coach.media.voice.premium": (
        "🎤 <b>Voice analysis — Premium only</b>\n\n"
        "Send a <b>📷 photo</b> of your pet — it's free.\n\n"
        "⭐ Premium unlocks voice and video analysis with no limits."
    ),
    "coach.media.video.premium": (
        "🎥 <b>Video analysis — Premium only</b>\n\n"
        "Send a <b>📷 photo</b> of your pet — it's free.\n\n"
        "⭐ Premium unlocks video and voice analysis with no limits."
    ),
    "coach.media.too_large": "⚠️ File too large (max 20 MB). Try sending a shorter clip.",
    "coach.hub.active_thread": (
        "💬 <b>Trainer</b> · <i>{title}</i>\n\n"
        "{count} msg · ongoing\n\n"
        "Continue or ask a new question."
    ),
    "coach.hub.archive_btn": "📁 End consultation",
    "coach.new_thread.btn": "🆕 New topic",
    "coach.thread.archived": "✔ Consultation ended.",
    "coach.thread.title_default": "Consultation",
    "coach.role.owner": "Owner",
    "coach.role.trainer": "Trainer",
    "coach.summary.header": "Brief summary of the previous conversation:",
    # ── Voice-action (hands-free task reporting) ───────────────────────────────
    "voice_action.thinking": "🐾 <i>Analysing...</i>",
    "voice_action.marked": "✅ I marked the task <b>{task}</b> as completed!\n\n",
    "voice_action.all_done": "🎉 All tasks for today completed! Great workout!",
    # ── Stats ──────────────────────────────────────────────────────────────────
    "stats.header": "📊 <b>{name}'s stats</b>\n\n",
    "stats.days_with_us": "🗓 Days with Pepito: <b>{n}</b>\n",
    "stats.completed": "{emoji} Sessions completed: <b>{n}</b>\n\n",
    "stats.level": "🏆 Obedience level: <b>{level}</b>\n\n",
    "stats.motivate": "<i>Every session makes {name} better!</i> 🚀",
    "stats.analysis.premium.btn": "🧠 AI Pro ⭐",
    "stats.analysis.free.btn": "🧠 AI analysis",
    # ── Profile ────────────────────────────────────────────────────────────────
    "profile.header": "🐾 <b>{name}</b>\n\n",
    "profile.breed": "🐕 Breed: {val}\n",
    "profile.sex": "⚥ Sex: {val}\n",
    "profile.age": "🎂 Age: {val}\n",
    "profile.size": "📏 Size: {val}\n",
    "profile.weight": "⚖️ Weight: {val}\n\n",
    "profile.level": "🎓 Level: {val}/5\n",
    "profile.goal": "🎯 Goal: {val}\n",
    "profile.issues": "📋 Issues: {val}\n",
    "profile.schedule": "🗓 Schedule: {val}\n\n",
    "profile.training_count": "🔥 Sessions completed: <b>{n}</b>",
    "profile.weight.unit": "kg",
    "profile.weight.unknown": "not specified",
    "profile.issues.none": "none",
    "profile.schedule.unknown": "not specified",
    "profile.edit.btn": "✏️ Edit",
    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>PepitoPet Shop</b>",
    "shop.body": (
        "Natural treats made in-house — "
        "no additives or preservatives, real meat only.\n\n"
        "Choose a category:"
    ),
    "shop.cat.training.btn": "🎯 Training",
    "shop.cat.longplay.btn": "🦴 Chews",
    "shop.cat.by_size.btn": "🐶 By size",
    "shop.cat.all.btn": "🛒 Full shop",
    "shop.rec.puppy_named": "🐶 Puppy treats — for {name}",
    "shop.rec.small_named": "🐶 Treats for small breeds — for {name}",
    "shop.rec.puppy_small_free": "🐶 Treats for puppies and small dogs",
    "shop.rec.longplay_named": "🎁 Long-lasting chews — a reward for {name}",
    "shop.rec.longplay_free": "🦴 Long-lasting chews",
    "shop.rec.exercise_named": "🦴 Training treats for {name}'s exercises",
    "shop.rec.training_named": "🦴 Training treats for {name}",
    "shop.rec.training_free": "🦴 Training treats",
    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>Invite a friend — bonus for both!</b>",
    "invite.link_label": "🔗 Your link:",
    "invite.bonus": "🎁 Each friend gives <b>+{days} days Premium</b> — to you <i>and</i> them.",
    "invite.ladder.title": "🏆 <b>Reward path:</b>",
    "invite.count": "👥 Invited: <b>{n}</b>",
    "invite.next": "🎯 Until the next reward: <b>{n}</b> more",
    "invite.all_done": "👑 <b>All rewards claimed! You're a legend!</b>",
    "invite.share.btn": "📤 Share link",
    "invite.share.text": "Training my dog with Pepito AI trainer 🐾",
    "invite.base_tier": "1 friend   — +{days} days Premium (for both)",
    "invite.goal": "🎯 {needed} more to {next_label} ({reward})",
    "invite.current_goal": "← next goal",
    "invite.how.title": "❓ <b>How it works:</b>",
    "invite.how.1": "1. Share your link",
    "invite.how.2": "2. Friend launches the bot and fills in a profile",
    "invite.how.3": "3. You both get +{days} days Premium",
    # ── Referral push-notifications ────────────────────────────────────────────
    "referral.notify.base": (
        "🎉 A new friend joined via your link!\n"
        "+{days} days Premium added. Friends invited: <b>{count}</b>\n{ladder_hint}"
    ),
    "referral.notify.milestone": (
        "🏆 <b>{label}!</b>\n\n"
        "You've invited {count} friends and earned <b>{reward}</b>!\n{next_hint}"
    ),
    "referral.notify.next_hint": "🎯 Next goal: {next_label} → {next_reward}",
    "referral.notify.all_done": "👑 All rewards unlocked!",
    "referral.milestone.label.3": "3 friends",
    "referral.milestone.label.5": "5 friends",
    "referral.milestone.label.10": "10 friends",
    "referral.milestone.label.25": "25 friends",
    "referral.reward.days": "+{days} days",
    # ── Premium / Subscription ─────────────────────────────────────────────────
    "premium.active.title": "⭐ <b>Premium active</b>",
    "premium.active.expires": "Valid until: <b>{date}</b>",
    "premium.active.features": (
        "\n\nIncluded:\n"
        "💬 Unlimited trainer questions\n"
        "🧠 In-depth AI progress analysis\n"
        "🎁 Personalised treat recommendations"
    ),
    "premium.upsell.body": (
        "⭐ <b>Pepito Premium</b>\n\n"
        "💬 Trainer questions — no limits\n"
        "🧠 In-depth AI progress analysis\n"
        "🎁 Personalised treat recommendations\n\n"
        "<b>{price} Stars</b> / month · or invite 3 friends — free"
    ),
    "premium.upsell.btn": "⭐ {price} Stars",
    "premium.invoice.title": "Pepito Premium — 1 month",
    "premium.invoice.description": "Unlimited AI trainer, detailed reports and in-depth behaviour analysis.",
    "premium.invoice.label": "Premium 1 month",
    "premium.activated": (
        "🎉 <b>Premium activated!</b>\n\n"
        "Now available:\n"
        "💬 Unlimited trainer questions\n"
        "🧠 In-depth progress analysis\n"
        "🎁 Personalised treat recommendations\n\n"
        "Use /menu to get started."
    ),
    "premium.paysupport": "💬 <b>Payment support</b>\n\nPaid but no Premium? Need a refund? Contact support with the payment ID from your Telegram chat. We reply within a day.",
    "premium.terms": "📄 <b>Terms</b>\n\nPremium is a digital subscription to the Pepito AI dog trainer, paid in Telegram Stars. It renews automatically and can be cancelled any time in Telegram settings. Refunds: /paysupport. The bot does not replace a vet.",
    "premium.plan.premium_1m.btn": "1 mo · {stars}⭐",
    "premium.plan.premium_3m.btn": "3 mo · {stars}⭐",
    "premium.plan.premium_12m.btn": "12 mo · {stars}⭐",
    "premium.plans.btn": "Plans",
    "ai.remaining": "{n} of {limit} left today",
    "onboarding.q.name": "🐶 Hi! I'm Pepito, your dog trainer. What's your dog's name?",
    "onboarding.q.age": "How old is <b>{name}</b>?",
    "onboarding.q.breed": "Which breed? Pick one or send a photo.",
    "onboarding.q.breed_text": "Type the breed or send a photo of your dog 📷",
    "onboarding.q.goal": "What do you want to work on?",
    "onboarding.photo.fail": "Couldn't tell the breed 🤔 Please type it.",
    "onboarding.photo.guess": "Looks like: <b>{breed}</b>. Right?",
    "onboarding.btn.other": "Other",
    "onboarding.btn.photo": "📷 Photo",
    "onboarding.age.1": "Under 4 mo",
    "onboarding.age.2": "4–12 mo",
    "onboarding.age.3": "1–3 years",
    "onboarding.age.4": "3–7 years",
    "onboarding.age.5": "7+ years",
    "onboarding.goal.1": "Obedience",
    "onboarding.goal.2": "Behavior",
    "onboarding.goal.3": "Puppy",
    "onboarding.goal.4": "Activity",
    "onboarding.name.need_text": "Please type the name 🙂",
    "memory.btn": "🧠 Memory",
    "memory.title": "🧠 <b>What I remember about {name}</b>\n──────────",
    "memory.empty": "🧠 I don't remember anything about <b>{name}</b> yet. Tell me about your dog in chat or add a fact yourself.",
    "memory.add.btn": "➕ Add",
    "memory.add.prompt": "Write a fact about your dog in one phrase, e.g. “afraid of thunder”.",
    "memory.add.invalid": "Please send 3 to 160 characters 🙂",
    "memory.deleted": "Deleted",
    "edit_profile.btn.weight": "⚖️ Weight",
    "edit_profile.btn.birth": "🎂 Birthday",
    "edit_profile.btn.allergies": "🚫 Allergies",
    "edit_profile.btn.chronic": "🩺 Conditions",
    "edit_profile.field.weight.prompt": "Send the weight in kg, e.g. 12.5",
    "edit_profile.field.birth.prompt": "Send the birth date: 31.12.2023",
    "edit_profile.field.allergies.prompt": "List allergies separated by commas, or send “none”",
    "edit_profile.field.chronic.prompt": "List chronic conditions separated by commas, or send “none”",
    "edit_profile.error.invalid": "Couldn't parse that. Check the format and try again.",
    "profile.allergies": "🚫 Allergies: {val}\n",
    "profile.chronic": "🩺 Conditions: {val}\n",
    "menu.btn.health": "🩺 Health",
    "health.title": "🩺 <b>{name}'s health</b>\n──────────",
    "health.kind.vaccine": "Vaccine",
    "health.kind.ticks": "Ticks",
    "health.kind.worms": "Worms",
    "health.row.none": "{kind}: not logged",
    "health.row.overdue": "{kind}: ⚠️ overdue by {n} d",
    "health.row.today": "{kind}: ❗ today",
    "health.row.soon": "{kind}: ⏳ in {n} d ({date})",
    "health.row.later": "{kind}: ✅ until {date}",
    "health.add.prompt": "When was it done: {kind}?",
    "health.btn.today": "Today",
    "health.btn.date": "Date",
    "health.btn.back": "🔙 Back",
    "health.date.prompt": "Send the date as 31.10.2026",
    "health.date.invalid": "Couldn't read the date. Send a past date like 31.10.2026.",
    "health.saved": "✅ Logged: {kind}. Next time — {date}.",
    "health.push.soon": "🔔 {name}: {kind} in {n} d ({date})",
    "health.push.today": "🔔 {name}: due today — {kind}",
    "health.btn.done": "✅ Done",
    "health.btn.snooze": "⏰ +3 days",
    "health.snoozed": "OK, I'll remind you on {date}.",
    "menu.btn.tracker": "🔥 Tracker",
    "tracker.title": "🔥 <b>{name}'s tracker</b>\n──────────",
    "tracker.streak": "Streak: <b>{n}</b> days in a row",
    "tracker.streak.zero": "Streak: 0 for now. Train today and it starts!",
    "tracker.today.done": "Today: ✅ done",
    "tracker.today.todo": "Today: not yet",
    "tracker.freezes": "🧊 Freezes this week: {n}",
    "tracker.week": "This week: {days} workouts, {walks} walks ({minutes} min)",
    "tracker.badges": "Badges: {list}",
    "tracker.walk.btn": "🚶 {m} min",
    "tracker.walk.saved": "Walk logged: {m} min",
    "tracker.badge.new": "🎉 New badge: {badge}",
    "tracker.badge.streak_7": "🔥7 days",
    "tracker.badge.streak_30": "⚡30 days",
    "tracker.badge.streak_100": "🏆100 days",
    "tracker.badge.walks_10": "🚶10 walks",
    "report.weekly.stats": "📊 <b>Your week, {name}</b>\n\n🐶 {pet}\n🏋️ Workouts: {days}\n🚶 Walks: {walks} ({minutes} min)\n🔥 Streak: {streak} days\n\nGreat job! A new plan arrives on Monday.",
    "menu.btn.more": "⚙️ More",
    "menu.more.title": "Pick a section 👇",
    "media.verdict.vet_now": "🚨 <b>See a vet today</b>",
    "media.verdict.vet_soon": "⚠️ <b>Show your vet in the next few days</b>",
    "media.verdict.see": "🎯 <b>What I see:</b>",
    "media.verdict.steps": "🛠 <b>What to do:</b>",
    "media.verdict.disclaimer": "<i>This is not a diagnosis or a replacement for a vet.</i>",
    "card.unit.streak": "days in a row",
    "card.headline.streak": "{pet} never skips training",
    "card.badge.caption": "New badge",
    "card.week.caption": "workouts this week",
    "card.row.walks": "Walks",
    "card.row.minutes": "Walk minutes",
    "card.row.streak": "Streak, days",
    "card.row.age": "Age",
    "card.row.weight": "Weight",
    "card.row.allergies": "Allergies",
    "card.unit.kg": "kg",
    "card.passport.caption": "Dog passport",
    "card.nothing": "Nothing to share yet. Train today and the card will appear!",
    "card.drawing": "Drawing the card…",
    "card.error": "Couldn't draw the card. Try again a bit later.",
    "card.caption": "Here you go! Post it to Stories 🐶",
    "tracker.card.streak.btn": "📤 Streak",
    "tracker.card.week.btn": "📤 Week",
    "tracker.card.badge.btn": "📤 Badge",
    "profile.card.btn": "📤 Card",
    "nudge.renew.soon": "⏳ Premium ends in {n} days ({date}). Renew so {pet} keeps unlimited answers and memory?",
    "nudge.renew.last": "⏳ Premium ends tomorrow ({date}). Renew to keep unlimited answers and the memory about {pet}.",
    "nudge.renew.btn": "⭐ Renew",
    "nudge.evening": "🔥 {n}-day streak — you haven't trained with {pet} today. 5 minutes keeps it alive!",
    "nudge.season.ticks": "🕷 {pet}: tick season has started. Check after every walk and don't forget the treatment — log it in Health.",
    "nudge.season.heat": "☀️ Heat! Walk {pet} in the morning and evening, give plenty of water and test the pavement with your palm.",
    "nudge.season.reagents": "🧂 Winter and road salt: wash {pet}'s paws after walks and use protective wax.",
    "nudge.winback": "👋 {pet} misses training. Premium brings back unlimited questions, memory about your dog and cards. Coming back?",
    "nudge.winback.btn": "⭐ Come back",
    "settings.seasonal.on": "🌦 Season: on",
    "settings.seasonal.off": "🌦 Season: off",
    "settings.seasonal.toast.on": "Seasonal tips on",
    "settings.seasonal.toast.off": "Seasonal tips off",
    "profile.pdf.btn": "📄 For vet",
    "pdf.drawing": "Building the PDF…",
    "pdf.caption": "Passport for your vet. Data is reported by the owner.",
    "pdf.passport.title": "Pepito — dog passport",
    "pdf.passport.profile": "Profile",
    "pdf.passport.breed": "Breed",
    "pdf.passport.sex": "Sex",
    "pdf.passport.age": "Age",
    "pdf.passport.birth": "Date of birth",
    "pdf.passport.weight": "Weight",
    "pdf.passport.kg": "kg",
    "pdf.passport.health": "Health",
    "pdf.passport.allergies": "Allergies",
    "pdf.passport.chronic": "Chronic conditions",
    "pdf.passport.notes": "Notes",
    "pdf.passport.schedule": "Vaccines and treatments",
    "pdf.passport.last": "done",
    "pdf.passport.next": "next",
    "pdf.passport.history": "History",
    "pdf.passport.facts": "Known about the dog",
    "pdf.passport.disclaimer": "Generated {date} by Pepito (@pepitopetbot) from owner-reported data. Not a medical document.",
    "voice_action.walk": "🚶 Walk logged: {m} min. Streak: {n} days.",
    "pets.add.btn": "➕ Dog",
    "pets.limit.free": "🐶 Free covers one dog. Premium allows up to {n}, each with its own passport, plan and memory.",
    "pets.limit.max": "Up to {n} dogs.",
    "pets.switched": "Now working with {name}",
    "pets.added": "🐶 {name} added! Building the first plan…",
    "pets.locked": "This dog needs Premium (up to {n} dogs). Your data is kept.",
    "gift.btn": "🎁 Gift",
    "gift.choose": "🎁 Gift Premium to a friend. Pick a period:",
    "gift.ask_username": "Send your friend's @username. They must already use the bot.",
    "gift.notfound": "I can't find that user. Your friend must start the bot first, then send the @username again.",
    "gift.self": "You can't gift yourself 🙂 Send a friend's @username.",
    "gift.invoice.title": "Gift: Premium",
    "gift.invoice.description": "Premium for {name}, {days} days",
    "gift.sent": "🎁 Done! {name} got Premium for {days} days.",
    "gift.received": "🎁 You were gifted Premium for {days} days! Unlimited questions, memory and cards are on.",
    "weight.btn": "⚖️ Weight",
    "weight.empty": "⚖️ No weight logged for <b>{name}</b> yet.",
    "weight.title": "⚖️ <b>{name}</b>: {kg} kg",
    "weight.change": "Over a month: {delta} kg ({pct}%), was {prev} kg",
    "weight.alert.gain": "⚠️ Weight rose by more than 10% in a month. Show your dog to a vet.",
    "weight.alert.loss": "⚠️ Weight dropped by more than 10% in a month. Show your dog to a vet.",
    "weight.ask": "Send the new weight in kg, e.g. 12.5",
    "weight.saved": "✅ Logged: {kg} kg",
    "weight.nudge": "⚖️ Time to weigh {pet}: once a month is enough. It takes 10 seconds.",
    "premium.rub.premium_1m.btn": "1 mo · {rub}₽",
    "premium.rub.premium_3m.btn": "3 mo · {rub}₽",
    "premium.rub.premium_12m.btn": "12 mo · {rub}₽",
    "premium.refunded": (
        "✔ Your refund has been processed. Premium subscription deactivated.\n"
        "If this is an error, please contact support."
    ),
    "webapp.validation.name_empty": "Name cannot be empty",
    "webapp.validation.name_long": "Name must be at most 30 characters",
    "webapp.validation.breed_long": "Breed must be at most 40 characters",
    "webapp.validation.goal_long": "Goal must be at most 150 characters",
    "webapp.validation.level": "Invalid training level",
    "webapp.validation.age": "Invalid age category",
    "webapp.validation.reminder": "Format: HH:MM, e.g. 09:30",
    "webapp.validation.timezone": "Invalid timezone",
    "webapp.validation.language": "Invalid language",
    # ── Reminders ─────────────────────────────────────────────────────────────
    "reminder.title": "⏰ <b>Reminders</b>",
    "reminder.status.off": "🔕 <b>Off</b>",
    "reminder.status.off.desc": "Daily reminders are not active.",
    "reminder.status.on": "🔔 <b>On</b> — {time} ({tz}) every day",
    "reminder.status.default": "🔔 <b>On</b> — 10:00 ({tz}, default)",
    "reminder.status.on.desc": "Pepito will remind you to train your pet.",
    "reminder.input.prompt": (
        "⏰ <b>Reminders</b>\n\n"
        "Enter the time in <code>HH:MM</code> format in your timezone (<b>{tz}</b>).\n"
        "Examples: <code>09:00</code>, <code>18:30</code>\n\n"
        "<i>You can change your timezone in ✏️ Edit profile → 🌍 Timezone.</i>"
    ),
    "reminder.disabled": ("🔕 <b>Off</b>\nYou will no longer receive daily reminders."),
    "reminder.saved": "✅ <b>Done!</b> Reminder set for <b>{time} ({tz})</b> every day.",
    "reminder.error.format": (
        "⚠️ Invalid format. Enter time as <code>HH:MM</code>, e.g. <code>09:30</code>."
    ),
    "reminder.enable.btn": "🔔 Turn on",
    "reminder.change.btn": "✏️ Change time",
    "reminder.disable.btn": "🔕 Disable",
    "reminder.back.btn": "🔙 Back",
    "reminder.back_settings.btn": "🔙 Back",
    "reminder.settings.btn": "🔔 Reminders",
    "reminder.menu.btn": "🔙 Menu",
    "reminder.tz_missing": "⚠️ <b>Timezone not set</b> — using UTC+0. Set it so reminders arrive at the right time.",
    "reminder.tz_change.btn": "🌍 Set timezone",
    "reminder.push.friend": "friend",
    "reminder.push.text": "🐾 Hi, {name}!\n\nDon't forget to train with your pet today. Open /menu to see the plan.",
    "report.weekly.premium": (
        "📊 Weekly report, {name}!\n\n"
        "Total training days: <b>{days}</b>\n"
        "Keep it up! Open /menu for details."
    ),
    "report.weekly.free": (
        "📊 Weekly summary, {name}!\n\n"
        "Training days: <b>{days}</b>\n"
        "Get detailed analytics with Premium — /menu."
    ),
    # ── Help / Support ─────────────────────────────────────────────────────────
    "help.guide.title": "❓ <b>Pepito Guide</b>\n\n",
    "help.guide.plan.header": "🧠 <b>How training plans work</b>\n",
    "help.guide.plan.text": (
        "Pepito generates a plan every day based on your pet's profile. "
        "Tap «🏋️ Today's training» to get your task list.\n\n"
    ),
    "help.guide.streak.header": "✅ <b>Checkboxes & progress</b>\n",
    "help.guide.streak.text": (
        "Mark ○ → ✅ each exercise. Complete all tasks and the day counts — "
        "your training total grows.\n\n"
    ),
    "help.guide.shop.header": "🛍️ <b>Shop & rewards</b>\n",
    "help.guide.shop.text": (
        "After training Pepito recommends natural PepitoPet treats. "
        "Invite friends — earn bonuses: +30, +60, +90 and +180 days Premium at milestones.\n\n"
    ),
    "help.guide.premium.header": "⭐ <b>What Premium gives you</b>\n",
    "help.guide.premium.text": (
        "💬 Unlimited trainer questions\n"
        "🧠 In-depth AI progress analysis\n"
        "🎁 Personalised treat recommendations with your pet's name\n\n"
    ),
    "help.guide.commands": "<b>Commands:</b> /menu · /start · /reset",
    "help.support.btn": "💬 Support",
    "help.btn": "❓ Help",
    "help.back_settings.btn": "🔙 Settings",
    # ── Edit Profile ───────────────────────────────────────────────────────────
    "edit_profile.title": "✏️ <b>Edit Profile</b>\n\nWhat would you like to change?",
    "edit_profile.field.name.prompt": "Enter the new pet name in the chat:",
    "edit_profile.field.breed.prompt": "Enter the new breed in the chat:",
    "edit_profile.field.goal.prompt": "Write the new training goal in the chat:",
    "edit_profile.field.level.prompt": "Choose the new obedience level:",
    "edit_profile.field.age.prompt": "Choose the new age category:",
    "edit_profile.field.size.prompt": "Choose the new pet size:",
    "edit_profile.field.timezone.prompt": "🌍 Choose your timezone:",
    "edit_profile.saved": "✅ Updated: <b>{value}</b>",
    "edit_profile.edit_more.btn": "✏️ Edit more",
    "edit_profile.error.empty": "⚠️ Field cannot be empty. Please try again.",
    "edit_profile.error.too_long": "⚠️ Value too long — max 50 characters (yours: {n}).",
    "edit_profile.btn.name": "🐾 Name",
    "edit_profile.btn.breed": "🐕 Breed",
    "edit_profile.btn.goal": "🎯 Goal",
    "edit_profile.btn.level": "🎓 Level",
    "edit_profile.btn.age": "🎂 Age",
    "edit_profile.btn.size": "📏 Size",
    "edit_profile.btn.timezone": "🌍 Timezone",
    "edit_profile.cancel.btn": "🔙 Cancel",
    "edit_profile.level.1": "1 — Knows no commands",
    "edit_profile.level.2": "2 — Knows basics (sit, stand)",
    "edit_profile.level.3": "3 — Obeys indoors",
    "edit_profile.level.4": "4 — Obeys with distractions",
    "edit_profile.level.5": "5 — Excellently trained",
    "edit_profile.size.small": "Small (up to 10 kg)",
    "edit_profile.size.medium": "Medium (10–25 kg)",
    "edit_profile.size.large": "Large (25–45 kg)",
    "edit_profile.size.giant": "Giant (45+ kg)",
    "edit_profile.age.1": "Puppy (up to 4 months)",
    "edit_profile.age.2": "Puppy (4–12 months)",
    "edit_profile.age.3": "Young (1–3 years)",
    "edit_profile.age.4": "Adult (3–7 years)",
    "edit_profile.age.5": "Senior (7+ years)",
}
