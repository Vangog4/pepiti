"""Deutsch (de) — German translation."""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Pepito — KI-Hundetrainer</b>",
    "menu.main.choose": "Wähle einen Bereich:",
    "menu.btn.training": "🏋️ Heutiges Training",
    "menu.btn.week_plan": "📅 Wochenplan",
    "menu.btn.stats": "📊 Statistiken",
    "menu.btn.coach": "💬 Trainer fragen",
    "menu.btn.profile": "🐶 Mein Tier",
    "menu.btn.premium": "⭐ Premium holen",
    "menu.btn.premium.active": "⭐ Premium (aktiv)",
    "menu.btn.shop": "🛒 Shop",
    "menu.btn.invite": "🐾 Freund einladen",
    "menu.btn.webapp": "📊 Dashboard",
    "menu.main.streak": "{emoji} Trainings absolviert: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "Tag",
    "menu.main.streak.days.few": "Tage",
    "menu.main.streak.days.many": "Tage",

    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 Hauptmenü",
    "common.back.btn": "🔙 Zurück",
    "common.menu.btn": "🔙 Menü",

    # ── Errors / Guards ────────────────────────────────────────────────────────
    "error.no_pet": "Bitte zuerst die Registrierung abschließen: /start",

    # ── Settings ───────────────────────────────────────────────────────────────
    "settings.main.title": "⚙️ <b>Einstellungen</b>",
    "settings.main.reminder_on": "⏰ Erinnerungen: <b>{time} ({tz})</b>",
    "settings.main.reminder_default": "⏰ Erinnerungen: <b>10:00 ({tz})</b> (Standard)",
    "settings.main.reminder_off": "⏰ Erinnerungen: <b>deaktiviert</b>",
    "settings.language.title": "🌐 <b>Sprache</b>",
    "settings.language.choose": "Wähle eine Sprache:",
    "settings.language.saved": "✅ Sprache geändert zu <b>{name}</b>.",
    "settings.language.btn": "🌐 Sprache",
    "settings.btn": "⚙️ Einstellungen",
    "settings.reminder.btn": "⏰ Erinnerungen",

    # ── Onboarding (Stage 9: conversational AI) ────────────────────────────────
    "onboarding.start.returning": "Willkommen zurück, {name}! 🐾\nWas machen wir heute?",
    "onboarding.ai.welcome": (
        "Hallo, <b>{name}</b>! Ich bin Pepito — dein KI-Hundetrainer. 🐶\n\n"
        "Erzähl mir von deinem Hund: Name, Rasse, Alter und welche Herausforderungen ihr habt?\n\n"
        "<i>Du kannst tippen oder eine Sprachnachricht senden.</i>\n\n"
        "<b>Beispiel:</b> «Beagle Charlie, 2 Jahre, zieht an der Leine und bellt andere Hunde an»"
    ),
    "onboarding.ai.thinking": "⏳ <i>Analysiere...</i>",
    "onboarding.ai.photo_prompt": (
        "📷 Süßes Tier! Erzähl mir mehr per Text oder Sprachnachricht:\n"
        "Name, Rasse, Alter und wobei du Hilfe brauchst?"
    ),
    "onboarding.ai.clarify": "Notiert — <b>{summary}</b>\n\n{question}",
    "onboarding.ai.clarify.name": "Wie heißt dein Haustier?",
    "onboarding.ai.clarify.breed": "Welche Rasse ist es?",
    "onboarding.ai.clarify.age_category": "Wie alt ist es? (Welpe, jung oder erwachsen?)",
    "onboarding.done.welcome": (
        "🎉 <b>Profil erstellt!</b>\n\n"
        "Willkommen, {name}!\n"
        "Ich bin bereit, dir beim Training von <b>{pet}</b> zu helfen."
    ),
    "onboarding.done.referral_bonus": "\n\n🎁 <b>Empfehlungsbonus:</b> +{days} Tage Premium aktiviert!",
    "onboarding.done.milestone": "\n🏆 <b>Empfehlungsmeilenstein:</b> {label} — {reward}!",
    "onboarding.done.plan_loading": "🐾 <i>Erstelle den ersten Trainingsplan für {pet}...</i>",
    "onboarding.done.first_plan": "🏋️ <b>Hier ist dein erster Plan!</b>\n\n{plan}",
    "onboarding.done.fallback": "Wähle, womit du beginnen möchtest 👇",

    # ── Training ───────────────────────────────────────────────────────────────
    "training.loading": "🐾 <i>Erstelle einen Plan für {name}...</i>",
    "training.refresh.confirm": "🔄 <b>Neuen Plan erstellen?</b>\n\nDein aktueller Fortschritt wird zurückgesetzt.",
    "training.refresh.confirm.yes": "✅ Ja, neuer Plan",
    "training.refresh.confirm.no": "❌ Nein",
    "training.refresh.loading": "🔄 <i>Erstelle neuen Plan für {name}...</i>",
    "training.refresh.toast": "Neuer Plan wird erstellt…",
    "training.week.loading": "📅 <i>Erstelle Wochenplan für {name}...</i>",
    "training.week.refresh.confirm": (
        "🔄 <b>Neuen Wochenplan erstellen?</b>\n\n"
        "Dein aktueller Wochenfortschritt wird zurückgesetzt."
    ),
    "training.week.refresh.loading": "🔄 <i>Erstelle neuen Wochenplan für {name}...</i>",
    "training.week.empty": (
        "📅 <b>Wochenplan</b>\n\n"
        "🌱 <b>Noch keine Aufgaben</b>\n\n"
        "Starte mit dem Tagesplan — Pepito erstellt den Wochenplan, "
        "sobald du etwas Fortschritt hast!"
    ),
    "training.week.empty.cta.btn": "🏋️ Heutiges Training",
    "training.explain.btn": "📖 Erklären",
    "training.refresh.btn": "🔄 Neuer Plan",
    "training.explain.loading": "🔍 <i>Erkläre Übung «{title}»...</i>",
    "training.explain.back_daily.btn": "🔙 Zurück zum Training",
    "training.explain.back_weekly.btn": "🔙 Zurück zum Plan",
    "training.task.not_found": "Aufgabe nicht gefunden.",
    "training.plan.not_found": "Plan nicht gefunden.",
    "training.task.toggle.done": "✅ Erledigt!",
    "training.task.toggle.undone": "↩️ Rückgängig",
    "training.share.text": "{name} und ich haben {n} {days} in Folge mit Pepito trainiert! 🐾",
    "training.share.btn": "📤 Teilen",
    "training.done": (
        "\n\n🎉 <b>Training abgeschlossen! Super gemacht!</b>\n"
        "{emoji} Trainings gesamt: {n}"
    ),
    "training.week_done": (
        "\n\n🎉 <b>{day} abgeschlossen! Super gemacht!</b>\n"
        "{emoji} Trainings gesamt: {n}"
    ),
    "training.stats.empty": (
        "🌱 <b>Du fängst gerade erst an!</b>\n\n"
        "Deine erste Einheit ist die wichtigste.\n"
        "Öffne den heutigen Plan und markiere die erste Übung als erledigt — "
        "dein Trainingsfortschritt beginnt zu wachsen!"
    ),
    "training.stats.empty.cta": "🏋️ Training starten",
    "training.minutes.abbr": "Min",
    "training.goal.label": "Ziel",
    "training.day.1": "Montag",
    "training.day.2": "Dienstag",
    "training.day.3": "Mittwoch",
    "training.day.4": "Donnerstag",
    "training.day.5": "Freitag",
    "training.day.6": "Samstag",
    "training.day.7": "Sonntag",
    "training.day.short.1": "Mo",
    "training.day.short.2": "Di",
    "training.day.short.3": "Mi",
    "training.day.short.4": "Do",
    "training.day.short.5": "Fr",
    "training.day.short.6": "Sa",
    "training.day.short.7": "So",
    "coach.display.photo": "[📷 Foto]",
    "coach.display.voice": "[🎤 Sprachnachricht]",
    "coach.display.video": "[🎥 Video]",
    "defaults.pet_name": "Tier",

    # ── AI / Coach ─────────────────────────────────────────────────────────────
    "ai.fallback": (
        "🧠 <b>Der Trainer bearbeitet gerade zu viele Anfragen</b>\n\n"
        "Versuche es gleich erneut — das löst sich meistens schnell.\n"
        "<i>Wenn das Problem anhält, gib /menu ein und versuche es erneut.</i>"
    ),
    "ai.rate_limit": (
        "💬 <b>Tageslimit erreicht</b>\n\n"
        "Kostenlos: <b>5 KI-Anfragen pro Tag</b>\n"
        "Limit wird um Mitternacht UTC zurückgesetzt.\n\n"
        "⭐ <b>Premium — unbegrenzt:</b>\n"
        "💬 Unbegrenzte Trainerfragen\n"
        "🧠 Detaillierte Fortschrittsanalyse\n"
        "🎁 Personalisierte Empfehlungen"
    ),
    "ai.rate_limit.btn": "⭐ Premium testen",
    "ai.analyzing.premium": "🧠 <i>Führe detaillierte Analyse durch...</i>",
    "ai.analyzing.free": "🧠 <i>Analysiere Fortschritt...</i>",
    "ai.progress.premium.header": "⭐ <b>Detaillierte Analyse für {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Fortschrittsanalyse für {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 Zurück zur Statistik",
    "ai.retry.btn": "🔄 Erneut versuchen",
    "ai.back_menu.btn": "🔙 Menü",
    "coach.entry": (
        "💬 <b>Trainer fragen</b>\n\n"
        "Stelle eine Frage zu Training oder Verhalten — oder sende ein <b>📷 Foto</b>.\n"
        "<i>z.B.: «Wie stoppe ich das Ziehen an der Leine?» oder «Warum ignoriert er „Platz“?»</i>\n\n"
        "Kostenlos: Text + Foto\n"
        "⭐ Premium: + 🎤 Sprachnachrichten und 🎥 Videos"
    ),
    "coach.thinking": "🧠 <i>Analysiere deine Frage...</i>",
    "coach.media.thinking": "🔍 <i>Analysiere Medien...</i>",
    "coach.media.voice.premium": (
        "🎤 <b>Sprachanalyse — nur Premium</b>\n\n"
        "Sende ein <b>📷 Foto</b> deines Hundes — kostenlos.\n\n"
        "⭐ Premium schaltet Sprach- und Videoanalyse ohne Limits frei."
    ),
    "coach.media.video.premium": (
        "🎥 <b>Videoanalyse — nur Premium</b>\n\n"
        "Sende ein <b>📷 Foto</b> deines Hundes — kostenlos.\n\n"
        "⭐ Premium schaltet Video- und Sprachanalyse ohne Limits frei."
    ),
    "coach.media.too_large": "⚠️ Datei zu groß (max 20 MB). Sende einen kürzeren Clip.",
    "coach.hub.active_thread": (
        "💬 <b>Trainer</b> · <i>{title}</i>\n\n"
        "{count} Nachr. · läuft\n\n"
        "Frage stellen oder Foto senden."
    ),
    "coach.hub.archive_btn": "📁 Beratung beenden",
    "coach.new_thread.btn": "🆕 Neue Beratung",
    "coach.thread.archived": "✔ Beratung abgeschlossen.",
    "coach.thread.title_default": "Beratung",
    "coach.role.owner": "Besitzer",
    "coach.role.trainer": "Trainer",
    "coach.summary.header": "Kurze Zusammenfassung des vorherigen Gesprächs:",

    # ── Voice-action (hands-free task reporting) ───────────────────────────────
    "voice_action.thinking": "🐾 <i>Analysiere...</i>",
    "voice_action.marked": "✅ Aufgabe <b>{task}</b> als erledigt markiert!\n\n",
    "voice_action.all_done": "🎉 Alle Aufgaben des Tages erledigt! Tolles Training!",

    # ── Stats ──────────────────────────────────────────────────────────────────
    "stats.header": "📊 <b>Statistik von {name}</b>\n\n",
    "stats.days_with_us": "🗓 Tage mit Pepito: <b>{n}</b>\n",
    "stats.completed": "{emoji} Abgeschlossene Einheiten: <b>{n}</b>\n\n",
    "stats.level": "🏆 Gehorsamkeitsniveau: <b>{level}</b>\n\n",
    "stats.motivate": "<i>Jede Einheit macht {name} besser!</i> 🚀",
    "stats.analysis.premium.btn": "🧠 Detaillierte KI-Analyse ⭐",
    "stats.analysis.free.btn": "🧠 KI-Fortschrittsanalyse",

    # ── Profile ────────────────────────────────────────────────────────────────
    "profile.header": "🐾 <b>{name}</b>\n\n",
    "profile.breed": "🐕 Rasse: {val}\n",
    "profile.sex": "⚥ Geschlecht: {val}\n",
    "profile.age": "🎂 Alter: {val}\n",
    "profile.size": "📏 Größe: {val}\n",
    "profile.weight": "⚖️ Gewicht: {val}\n\n",
    "profile.level": "🎓 Niveau: {val}/5\n",
    "profile.goal": "🎯 Ziel: {val}\n",
    "profile.issues": "📋 Probleme: {val}\n",
    "profile.schedule": "🗓 Zeitplan: {val}\n\n",
    "profile.training_count": "🔥 Abgeschlossene Einheiten: <b>{n}</b>",
    "profile.weight.unit": "kg",
    "profile.weight.unknown": "nicht angegeben",
    "profile.issues.none": "keine",
    "profile.schedule.unknown": "nicht angegeben",
    "profile.edit.btn": "✏️ Profil bearbeiten",

    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>PepitoPet Shop</b>",
    "shop.body": (
        "Hausgemachte Naturleckerlis — "
        "ohne Zusatzstoffe oder Konservierungsmittel, nur echtes Fleisch.\n\n"
        "Kategorie wählen:"
    ),
    "shop.cat.training.btn": "🎯 Trainingleckerlis",
    "shop.cat.longplay.btn": "🦴 Langzeit-Kauartikel",
    "shop.cat.by_size.btn": "🐶 Welpen & nach Größe",
    "shop.cat.all.btn": "🛒 Ganzer Shop",

    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>Freund einladen — Bonus für beide!</b>",
    "invite.link_label": "🔗 Dein Link:",
    "invite.bonus": "🎁 Jeder Freund gibt <b>+{days} Tage Premium</b> — dir <i>und</i> ihm.",
    "invite.ladder.title": "🏆 <b>Belohnungsweg:</b>",
    "invite.count": "👥 Eingeladen: <b>{n}</b>",
    "invite.next": "🎯 Bis zur nächsten Belohnung: noch <b>{n}</b>",
    "invite.all_done": "👑 <b>Alle Belohnungen erhalten! Du bist eine Legende!</b>",
    "invite.share.btn": "📤 Link teilen",
    "invite.share.text": "Ich trainiere mein Tier mit Pepito KI-Trainer 🐾",
    "invite.base_tier": "1 Freund   — +{days} Tage Premium (für beide)",
    "invite.goal": "🎯 Noch {needed} bis {next_label} ({reward})",
    "invite.current_goal": "← nächstes Ziel",
    "invite.how.title": "❓ <b>So funktioniert es:</b>",
    "invite.how.1": "1. Teile deinen Link",
    "invite.how.2": "2. Freund startet den Bot und füllt das Profil aus",
    "invite.how.3": "3. Ihr bekommt beide +{days} Tage Premium",

    # ── Referral push-notifications ────────────────────────────────────────────
    "referral.notify.base": (
        "🎉 Ein neuer Freund ist über deinen Link beigetreten!\n"
        "+{days} Tage Premium hinzugefügt. Eingeladen: <b>{count}</b>\n{ladder_hint}"
    ),
    "referral.notify.milestone": (
        "🏆 <b>{label}!</b>\n\n"
        "Du hast {count} Freunde eingeladen und erhältst <b>{reward}</b>!\n{next_hint}"
    ),
    "referral.notify.next_hint": "🎯 Nächstes Ziel: {next_label} → {next_reward}",
    "referral.notify.all_done": "👑 Alle Belohnungen freigeschaltet!",
    "referral.milestone.label.3":  "3 Freunde",
    "referral.milestone.label.5":  "5 Freunde",
    "referral.milestone.label.10": "10 Freunde",
    "referral.milestone.label.25": "25 Freunde",
    "referral.reward.days": "+{days} Tage",

    # ── Premium / Subscription ─────────────────────────────────────────────────
    "premium.active.title": "⭐ <b>Premium aktiv</b>",
    "premium.active.expires": "Gültig bis: <b>{date}</b>",
    "premium.active.features": (
        "\n\nEnthalten:\n"
        "💬 Unbegrenzte Trainerfragen\n"
        "🧠 Detaillierte KI-Fortschrittsanalyse\n"
        "🎁 Personalisierte Leckerli-Empfehlungen"
    ),
    "premium.upsell.body": (
        "⭐ <b>Pepito Premium</b>\n\n"
        "💬 Trainerfragen — ohne Limit\n"
        "🧠 Detaillierte KI-Fortschrittsanalyse\n"
        "🎁 Personalisierte Leckerli-Empfehlungen\n\n"
        "<b>{price} Stars</b> / Monat · oder 3 Freunde einladen — kostenlos"
    ),
    "premium.upsell.btn": "⭐ Premium für {price} Stars holen",
    "premium.invoice.title": "Pepito Premium — 1 Monat",
    "premium.invoice.description": "Unbegrenzter KI-Trainer, detaillierte Berichte und tiefgehende Verhaltensanalyse.",
    "premium.invoice.label": "Premium 1 Monat",
    "premium.activated": (
        "🎉 <b>Premium aktiviert!</b>\n\n"
        "Jetzt verfügbar:\n"
        "💬 Unbegrenzte Trainerfragen\n"
        "🧠 Detaillierte Fortschrittsanalyse\n"
        "🎁 Personalisierte Leckerli-Empfehlungen\n\n"
        "Nutze /menu zum Starten."
    ),
    "premium.refunded": (
        "✔ Deine Rückerstattung wurde verarbeitet. Premium-Abonnement deaktiviert.\n"
        "Wenn das ein Fehler ist, wende dich bitte an den Support."
    ),

    # ── Reminders ─────────────────────────────────────────────────────────────
    "reminder.title": "⏰ <b>Erinnerungen</b>",
    "reminder.status.off": "🔕 <b>Aus</b>",
    "reminder.status.off.desc": "Tägliche Erinnerungen sind nicht aktiv.",
    "reminder.status.on": "🔔 <b>An</b> — {time} ({tz}) täglich",
    "reminder.status.default": "🔔 <b>An</b> — 10:00 ({tz}, Standard)",
    "reminder.status.on.desc": "Pepito erinnert dich ans Training.",
    "reminder.input.prompt": (
        "⏰ <b>Erinnerungen</b>\n\n"
        "Gib die Uhrzeit im Format <code>HH:MM</code> in deiner Zeitzone (<b>{tz}</b>) ein.\n"
        "Beispiele: <code>09:00</code>, <code>18:30</code>\n\n"
        "<i>Du kannst deine Zeitzone unter ✏️ Profil bearbeiten → 🌍 Zeitzone ändern.</i>"
    ),
    "reminder.disabled": (
        "🔕 <b>Aus</b>\n"
        "Du erhältst keine täglichen Erinnerungen mehr."
    ),
    "reminder.saved": "✅ <b>Fertig!</b> Erinnerung gesetzt für <b>{time} ({tz})</b> täglich.",
    "reminder.error.format": (
        "⚠️ Ungültiges Format. Gib die Zeit als <code>HH:MM</code> ein, z.B. <code>09:30</code>."
    ),
    "reminder.enable.btn": "🔔 Erinnerungen aktivieren",
    "reminder.change.btn": "✏️ Zeit ändern",
    "reminder.disable.btn": "🔕 Deaktivieren",
    "reminder.back.btn": "🔙 Zurück zu Erinnerungen",
    "reminder.back_settings.btn": "🔙 Zurück",
    "reminder.settings.btn": "⏰ Erinnerungseinstellungen",
    "reminder.menu.btn": "🔙 Menü",
    "reminder.tz_missing": "⚠️ <b>Zeitzone nicht gesetzt</b> — UTC+0 wird verwendet. Stelle sie ein, damit Erinnerungen zur richtigen Zeit kommen.",
    "reminder.tz_change.btn": "🌍 Zeitzone festlegen",
    "reminder.push.friend": "Freund",
    "reminder.push.text": "🐾 Hallo, {name}!\n\nVergiss nicht, heute mit deinem Haustier zu trainieren. Öffne /menu, um den Plan zu sehen.",
    "report.weekly.premium": (
        "📊 Wochenbericht, {name}!\n\n"
        "Trainingstage gesamt: <b>{days}</b>\n"
        "Weiter so! Öffne /menu für Details."
    ),
    "report.weekly.free": (
        "📊 Wochenzusammenfassung, {name}!\n\n"
        "Trainingstage: <b>{days}</b>\n"
        "Hol dir Premium für detaillierte Analysen — /menu."
    ),

    # ── Help / Support ─────────────────────────────────────────────────────────
    "help.guide.title": "❓ <b>Pepito-Leitfaden</b>\n\n",
    "help.guide.plan.header": "🧠 <b>Wie Trainingspläne funktionieren</b>\n",
    "help.guide.plan.text": (
        "Pepito erstellt täglich einen Plan basierend auf dem Profil deines Haustieres. "
        "Tippe auf «🏋️ Heutiges Training» für deine Aufgabenliste.\n\n"
    ),
    "help.guide.streak.header": "✅ <b>Checkboxen & Fortschritt</b>\n",
    "help.guide.streak.text": (
        "Markiere ○ → ✅ jede Übung. Alle Aufgaben erledigt und der Tag zählt — "
        "dein Trainingsfortschritt wächst.\n\n"
    ),
    "help.guide.shop.header": "🛍️ <b>Shop & Belohnungen</b>\n",
    "help.guide.shop.text": (
        "Nach dem Training empfiehlt Pepito natürliche PepitoPet-Leckerlis. "
        "Lade Freunde ein — verdiene Boni: +30, +60, +90 und +180 Tage Premium bei Meilensteinen.\n\n"
    ),
    "help.guide.premium.header": "⭐ <b>Was Premium bietet</b>\n",
    "help.guide.premium.text": (
        "💬 Unbegrenzte Trainerfragen\n"
        "🧠 Detaillierte KI-Fortschrittsanalyse\n"
        "🎁 Personalisierte Leckerli-Empfehlungen mit Tiernamen\n\n"
    ),
    "help.guide.commands": "<b>Befehle:</b> /menu · /start · /reset",
    "help.support.btn": "💬 Support kontaktieren",
    "help.btn": "❓ Hilfe",
    "help.back_settings.btn": "🔙 Zurück zu Einstellungen",

    # ── Edit Profile ───────────────────────────────────────────────────────────
    "edit_profile.title": "✏️ <b>Profil bearbeiten</b>\n\nWas möchtest du ändern?",
    "edit_profile.field.name.prompt": "Gib den neuen Namen deines Tieres ein:",
    "edit_profile.field.breed.prompt": "Gib die neue Rasse ein:",
    "edit_profile.field.goal.prompt": "Schreibe das neue Trainingsziel in den Chat:",
    "edit_profile.field.level.prompt": "Wähle die neue Gehorsamkeitsstufe:",
    "edit_profile.field.age.prompt": "Wähle die neue Alterskategorie:",
    "edit_profile.field.size.prompt": "Wähle die neue Größe des Tieres:",
    "edit_profile.field.timezone.prompt": "🌍 Wähle deine Zeitzone:",
    "edit_profile.saved": "✅ Aktualisiert: <b>{value}</b>",
    "edit_profile.edit_more.btn": "✏️ Mehr bearbeiten",
    "edit_profile.error.empty": "⚠️ Das Feld darf nicht leer sein. Bitte erneut versuchen.",
    "edit_profile.error.too_long": "⚠️ Wert zu lang — max. 50 Zeichen (dein Wert: {n}).",
    "edit_profile.btn.name": "🐾 Name",
    "edit_profile.btn.breed": "🐕 Rasse",
    "edit_profile.btn.goal": "🎯 Ziel",
    "edit_profile.btn.level": "🎓 Level",
    "edit_profile.btn.age": "🎂 Alter",
    "edit_profile.btn.size": "📏 Größe",
    "edit_profile.btn.timezone": "🌍 Zeitzone",
    "edit_profile.cancel.btn": "🔙 Abbrechen",
    "edit_profile.level.1": "1 — Kennt keine Befehle",
    "edit_profile.level.2": "2 — Kennt Grundlagen (sitzen, stehen)",
    "edit_profile.level.3": "3 — Gehorcht drinnen",
    "edit_profile.level.4": "4 — Gehorcht bei Ablenkungen",
    "edit_profile.level.5": "5 — Ausgezeichnet trainiert",
    "edit_profile.size.small": "Klein (bis 10 kg)",
    "edit_profile.size.medium": "Mittel (10–25 kg)",
    "edit_profile.size.large": "Groß (25–45 kg)",
    "edit_profile.size.giant": "Riesig (45+ kg)",
    "edit_profile.age.1": "Welpe (bis 4 Monate)",
    "edit_profile.age.2": "Welpe (4–12 Monate)",
    "edit_profile.age.3": "Jung (1–3 Jahre)",
    "edit_profile.age.4": "Erwachsen (3–7 Jahre)",
    "edit_profile.age.5": "Senior (7+ Jahre)",
}
