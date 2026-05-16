(function () {
  "use strict";

  // Guard: must be opened inside Telegram via the bot's Dashboard button
  if (!window.Telegram?.WebApp?.initData) {
    const el = document.getElementById("state-loading");
    if (el) {
      el.innerHTML = (
        '<div class="state-emoji">📱</div>' +
        '<h3 class="state-title">Открыть через бота · Open via bot</h3>' +
        '<p class="state-subtitle">' +
          'Нажмите кнопку <b>📊 Dashboard</b> в боте @pepitopetbot<br>' +
          'Tap the <b>📊 Dashboard</b> button in @pepitopetbot' +
        '</p>' +
        '<a class="btn-primary" style="display:inline-block;margin-top:16px;padding:12px 24px;border-radius:12px;text-decoration:none;color:#fff;background:var(--tg-theme-button-color,#6c63ff)" ' +
          'href="https://t.me/pepitopetbot">Открыть бота · Open bot</a>'
      );
    }
    return;
  }

  const tg = window.Telegram.WebApp;
  tg.ready();
  tg.expand();

  // ── i18n ───────────────────────────────────────────────────────────
  const WEBAPP_I18N = {
    ru: {
      days: ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"],
      greet: "Привет",
      min_abbr: "мин",
      level_1: "Нач.", level_2: "База", level_3: "Ср.", level_4: "Хор.", level_5: "Проф.",
      diff_easy: "лёгкое", diff_medium: "среднее", diff_hard: "сложное",
      err_name_empty: "Имя не может быть пустым",
      err_name_long: "Не более 30 символов",
      err_goal_long: "Не более 150 символов",
      err_reminder_fmt: "Формат: ЧЧ:ММ — например 09:30",
      saving: "Сохранение...",
      saved: "✓ Сохранено",
      save_error: "✗ Ошибка — попробуй ещё раз",
      lang_saved: "✓ Сохранено",
      lang_error: "✗ Ошибка",
      day_abbr: "дн.",
      milestones_done: "Все награды получены! Ты легенда! 🏆",
      progress_need: "Ещё {n} до {reward}",
      goal_reached: "Цель достигнута!",
      expires_prefix: "до ",
      locale_code: "ru-RU",
      shop_training_title: "Для дрессировки",
      shop_training_desc: "Мелкие лакомства для обучения командам",
      shop_longplay_title: "Долгоиграющие",
      shop_longplay_desc: "Жевательные лакомства для самостоятельной игры",
      shop_bysize_title: "Для малышей",
      shop_bysize_desc: "Щенки и маленькие породы — подобраны по размеру",
      shop_open_btn: "Открыть →",
      copy_ok: "✓ Ссылка скопирована",
      copy_fail: "✗ Не удалось скопировать",
      share_text: "Тренируй питомца с AI-кинологом Pepito! 🐾",
      coach_load_error: "Не удалось загрузить консультации. Попробуйте позже.",
      thread_default_title: "Консультация",
      thread_active: "Активно",
      thread_archived: "Архив",
      thread_click_active: "💬 Тема «{title}» активна. Перейдите в чат с ботом, чтобы продолжить консультацию.",
      thread_click_archived: "📁 Тема «{title}» архивирована. Начните новую консультацию в боте.",
      thread_archive_btn: "🗂 В архив",
      thread_archive_error: "Не удалось архивировать. Попробуйте ещё раз.",
      date_today: "сегодня",
      date_yesterday: "вчера",
      date_days_ago: "{n} дн. назад",
      date_locale: "ru-RU",
      msg_1: "сообщение", msg_2: "сообщения", msg_many: "сообщений",
      stat_done_lbl: "выполнено", stat_done_sub: "сегодня",
      stat_days_lbl: "тренировок", stat_days_sub: "всего",
      card_progress_title: "Прогресс дня", card_training_title: "Тренировка сегодня",
      no_plan_title: "Нет плана на сегодня", no_plan_hint: "Открой бота и создай тренировку",
      all_done_title: "Все задачи выполнены!", all_done_sub: "Отличная тренировка сегодня",
      profile_heading: "✏️ Профиль питомца", no_pet_title: "Профиль не заполнен",
      no_pet_hint: "Пройди онбординг в боте, чтобы заполнить данные питомца",
      lbl_pet_name: "Имя питомца", lbl_breed: "Порода", lbl_goal: "Цель тренировок",
      lbl_level: "Уровень", lbl_age: "Возраст", btn_save_pet: "Сохранить изменения",
      select_default: "— выбери —",
      age_1: "до 4 мес", age_2: "4–12 мес", age_3: "1–3 года", age_4: "3–7 лет", age_5: "7+ лет",
      settings_heading: "⚙️ Настройки", card_notif_title: "Уведомления",
      lbl_reminder: "Время напоминания", hint_reminder_tz: "Местное время — в выбранном часовом поясе ниже",
      lbl_tz: "Часовой пояс", btn_save_settings: "Сохранить", card_lang_title: "Язык интерфейса бота",
      prem_hint_title: "Расширенная аналитика", prem_hint_sub: "Доступно в Premium",
      prem_hint_desc: "Глубокий AI-анализ прогресса, персональные рекомендации для питомца и детальная статистика.",
      btn_premium_hint: "Узнать больше в боте",
      rewards_heading: "🎁 Награды", card_invite_title: "Позови друга",
      ref_friends_lbl: "друзей приведено", how_works_title: "Как это работает",
      how_step_1: "Поделись ссылкой с другом",
      how_step_2: "Друг регистрируется и заполняет профиль питомца",
      how_step_3: "Вы оба получаете {days} Premium бесплатно",
      how_step_4: "Приглашай больше — получай milestone-бонусы!",
      prem_ben_1: "♾️ Безлимитный AI-кинолог", prem_ben_2: "🧠 Глубокий анализ прогресса",
      prem_ben_3: "🎥 Анализ видео и 🎤 голосовых кинологом", prem_ben_4: "🎁 Персональные рекомендации лакомств",
      btn_buy_premium: "⭐ Получить Premium", prem_active_lbl: "PREMIUM АКТИВЕН",
      prem_expiry_warn: "⚠️ Истекает скоро — продли в боте", card_shop_title: "Магазин лакомств",
      coach_heading: "💬 Консультации", coach_subheading: "История диалогов с AI-кинологом",
      coach_empty_title: "Консультаций пока нет",
      coach_empty_hint: "Задайте вопрос AI-кинологу в боте — темы сохраняются здесь как ценные записи",
      tab_lbl_pet: "Питомец", tab_lbl_settings: "Настройки",
      tab_lbl_rewards: "Награды", tab_lbl_coach: "Кинолог",
      btn_retry: "Попробовать снова", loading_text: "Загружаем...",
      ref_no_link: "Открой <b>🐾 Позови друга</b> в боте, чтобы получить ссылку.",
      btn_copy_ref: "📋 Скопировать", btn_share_ref: "📤 Поделиться",
      error_title: "Что-то пошло не так", error_msg: "Попробуй открыть дашборд снова",
    },
    en: {
      days: ["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
      greet: "Hello",
      min_abbr: "min",
      level_1: "Beg.", level_2: "Base", level_3: "Mid.", level_4: "Good", level_5: "Pro",
      diff_easy: "easy", diff_medium: "medium", diff_hard: "hard",
      err_name_empty: "Name cannot be empty",
      err_name_long: "Max 30 characters",
      err_goal_long: "Max 150 characters",
      err_reminder_fmt: "Format: HH:MM — e.g. 09:30",
      saving: "Saving...",
      saved: "✓ Saved",
      save_error: "✗ Error — please try again",
      lang_saved: "✓ Saved",
      lang_error: "✗ Error",
      day_abbr: "d.",
      milestones_done: "All milestone rewards earned 🏆",
      progress_need: "{n} more to {reward}",
      goal_reached: "Goal reached!",
      expires_prefix: "until ",
      locale_code: "en-GB",
      shop_training_title: "For training",
      shop_training_desc: "Small treats for command training",
      shop_longplay_title: "Long-lasting",
      shop_longplay_desc: "Chew treats for independent play",
      shop_bysize_title: "For small dogs",
      shop_bysize_desc: "Puppies and small breeds — sized to fit",
      shop_open_btn: "Open →",
      copy_ok: "✓ Link copied",
      copy_fail: "✗ Could not copy",
      share_text: "Train your pet with AI coach Pepito! 🐾",
      coach_load_error: "Could not load sessions. Please try later.",
      thread_default_title: "Consultation",
      thread_active: "Active",
      thread_archived: "Archived",
      thread_click_active: "💬 Thread «{title}» is active. Open the bot to continue.",
      thread_click_archived: "📁 Thread «{title}» is archived. Start a new consultation in the bot.",
      thread_archive_btn: "🗂 Archive",
      thread_archive_error: "Could not archive. Please try again.",
      date_today: "today",
      date_yesterday: "yesterday",
      date_days_ago: "{n} days ago",
      date_locale: "en-GB",
      msg_1: "message", msg_2: "messages", msg_many: "messages",
      stat_done_lbl: "completed", stat_done_sub: "today",
      stat_days_lbl: "sessions", stat_days_sub: "total",
      card_progress_title: "Day Progress", card_training_title: "Today's Training",
      no_plan_title: "No plan for today", no_plan_hint: "Open the bot to create a training",
      all_done_title: "All tasks completed!", all_done_sub: "Great training session today",
      profile_heading: "✏️ Pet Profile", no_pet_title: "Profile incomplete",
      no_pet_hint: "Complete onboarding in the bot to fill in pet data",
      lbl_pet_name: "Pet name", lbl_breed: "Breed", lbl_goal: "Training goal",
      lbl_level: "Level", lbl_age: "Age", btn_save_pet: "Save changes",
      select_default: "— select —",
      age_1: "up to 4 mo.", age_2: "4–12 mo.", age_3: "1–3 yr", age_4: "3–7 yr", age_5: "7+ yr",
      settings_heading: "⚙️ Settings", card_notif_title: "Notifications",
      lbl_reminder: "Reminder time", hint_reminder_tz: "Local time — in the selected timezone below",
      lbl_tz: "Timezone", btn_save_settings: "Save", card_lang_title: "Bot interface language",
      prem_hint_title: "Advanced analytics", prem_hint_sub: "Available in Premium",
      prem_hint_desc: "In-depth AI progress analysis, personalised recommendations for your pet and detailed statistics.",
      btn_premium_hint: "Learn more in bot",
      rewards_heading: "🎁 Rewards", card_invite_title: "Invite a friend",
      ref_friends_lbl: "friends invited", how_works_title: "How it works",
      how_step_1: "Share your link with a friend",
      how_step_2: "Friend signs up and fills in pet profile",
      how_step_3: "You both get {days} Premium for free",
      how_step_4: "Invite more — earn milestone bonuses!",
      prem_ben_1: "♾️ Unlimited AI trainer", prem_ben_2: "🧠 In-depth progress analysis",
      prem_ben_3: "🎥 Video and 🎤 voice analysis", prem_ben_4: "🎁 Personalised treat recommendations",
      btn_buy_premium: "⭐ Get Premium", prem_active_lbl: "PREMIUM ACTIVE",
      prem_expiry_warn: "⚠️ Expiring soon — renew in bot", card_shop_title: "Treat Shop",
      coach_heading: "💬 Consultations", coach_subheading: "History of AI trainer sessions",
      coach_empty_title: "No consultations yet",
      coach_empty_hint: "Ask the AI trainer in the bot — sessions are saved here as valuable records",
      tab_lbl_pet: "Pet", tab_lbl_settings: "Settings",
      tab_lbl_rewards: "Rewards", tab_lbl_coach: "Trainer",
      btn_retry: "Try again", loading_text: "Loading...",
      ref_no_link: "Open <b>🐾 Invite a friend</b> in the bot to get your link.",
      btn_copy_ref: "📋 Copy", btn_share_ref: "📤 Share",
      error_title: "Something went wrong", error_msg: "Try opening the dashboard again",
    },
    de: {
      days: ["So", "Mo", "Di", "Mi", "Do", "Fr", "Sa"],
      greet: "Hallo",
      min_abbr: "Min",
      level_1: "Anf.", level_2: "Basis", level_3: "Mitt.", level_4: "Gut", level_5: "Prof.",
      diff_easy: "leicht", diff_medium: "mittel", diff_hard: "schwer",
      err_name_empty: "Name darf nicht leer sein",
      err_name_long: "Max. 30 Zeichen",
      err_goal_long: "Max. 150 Zeichen",
      err_reminder_fmt: "Format: HH:MM — z.B. 09:30",
      saving: "Speichern...",
      saved: "✓ Gespeichert",
      save_error: "✗ Fehler — bitte erneut versuchen",
      lang_saved: "✓ Gespeichert",
      lang_error: "✗ Fehler",
      day_abbr: "T.",
      milestones_done: "Alle Meilenstein-Belohnungen erhalten 🏆",
      progress_need: "Noch {n} bis {reward}",
      goal_reached: "Ziel erreicht!",
      expires_prefix: "bis ",
      locale_code: "de-DE",
      shop_training_title: "Für das Training",
      shop_training_desc: "Kleine Leckerlis für die Befehlsausbildung",
      shop_longplay_title: "Langzeit-Snacks",
      shop_longplay_desc: "Kauspielzeug für selbstständiges Spielen",
      shop_bysize_title: "Für Kleine",
      shop_bysize_desc: "Welpen und kleine Rassen — größengerecht",
      shop_open_btn: "Öffnen →",
      copy_ok: "✓ Link kopiert",
      copy_fail: "✗ Kopieren fehlgeschlagen",
      share_text: "Trainiere dein Haustier mit dem KI-Coach Pepito! 🐾",
      coach_load_error: "Sitzungen konnten nicht geladen werden. Bitte später versuchen.",
      thread_default_title: "Beratung",
      thread_active: "Aktiv",
      thread_archived: "Archiviert",
      thread_click_active: "💬 Thema «{title}» ist aktiv. Öffne den Bot, um fortzufahren.",
      thread_click_archived: "📁 Thema «{title}» ist archiviert. Starte eine neue Beratung im Bot.",
      thread_archive_btn: "🗂 Archivieren",
      thread_archive_error: "Archivierung fehlgeschlagen. Bitte erneut versuchen.",
      date_today: "heute",
      date_yesterday: "gestern",
      date_days_ago: "vor {n} Tagen",
      date_locale: "de-DE",
      msg_1: "Nachricht", msg_2: "Nachrichten", msg_many: "Nachrichten",
      stat_done_lbl: "erledigt", stat_done_sub: "heute",
      stat_days_lbl: "Einheiten", stat_days_sub: "gesamt",
      card_progress_title: "Tagesfortschritt", card_training_title: "Heutiges Training",
      no_plan_title: "Kein Plan für heute", no_plan_hint: "Öffne den Bot und erstelle ein Training",
      all_done_title: "Alle Aufgaben erledigt!", all_done_sub: "Großartiges Training heute",
      profile_heading: "✏️ Haustierprofil", no_pet_title: "Profil unvollständig",
      no_pet_hint: "Schließe das Onboarding im Bot ab, um Haustierdaten zu ergänzen",
      lbl_pet_name: "Tiername", lbl_breed: "Rasse", lbl_goal: "Trainingsziel",
      lbl_level: "Stufe", lbl_age: "Alter", btn_save_pet: "Änderungen speichern",
      select_default: "— wähle —",
      age_1: "bis 4 Mon.", age_2: "4–12 Mon.", age_3: "1–3 J.", age_4: "3–7 J.", age_5: "7+ J.",
      settings_heading: "⚙️ Einstellungen", card_notif_title: "Benachrichtigungen",
      lbl_reminder: "Erinnerungszeit", hint_reminder_tz: "Ortszeit — in der unten gewählten Zeitzone",
      lbl_tz: "Zeitzone", btn_save_settings: "Speichern", card_lang_title: "Bot-Sprache",
      prem_hint_title: "Erweiterte Analytik", prem_hint_sub: "In Premium verfügbar",
      prem_hint_desc: "Detaillierte KI-Fortschrittsanalyse, personalisierte Empfehlungen für dein Haustier und detaillierte Statistiken.",
      btn_premium_hint: "Mehr im Bot erfahren",
      rewards_heading: "🎁 Belohnungen", card_invite_title: "Freund einladen",
      ref_friends_lbl: "Freunde eingeladen", how_works_title: "Wie es funktioniert",
      how_step_1: "Teile deinen Link mit einem Freund",
      how_step_2: "Freund registriert sich und füllt das Haustierprofil aus",
      how_step_3: "Ihr erhaltet beide {days} Premium kostenlos",
      how_step_4: "Lade mehr ein — erhalte Meilensteinboni!",
      prem_ben_1: "♾️ Unbegrenzte KI-Traineranfragen", prem_ben_2: "🧠 Detaillierte Fortschrittsanalyse",
      prem_ben_3: "🎥 Video- und 🎤 Sprachanalyse", prem_ben_4: "🎁 Personalisierte Leckerli-Empfehlungen",
      btn_buy_premium: "⭐ Premium erhalten", prem_active_lbl: "PREMIUM AKTIV",
      prem_expiry_warn: "⚠️ Läuft bald ab — im Bot verlängern", card_shop_title: "Leckerli-Shop",
      coach_heading: "💬 Beratungen", coach_subheading: "Verlauf der KI-Trainergespräche",
      coach_empty_title: "Noch keine Beratungen",
      coach_empty_hint: "Stelle dem KI-Trainer im Bot Fragen — Themen werden hier als wertvolle Einträge gespeichert",
      tab_lbl_pet: "Haustier", tab_lbl_settings: "Einstellungen",
      tab_lbl_rewards: "Belohnungen", tab_lbl_coach: "Trainer",
      btn_retry: "Erneut versuchen", loading_text: "Laden...",
      ref_no_link: "Öffne <b>🐾 Freund einladen</b> im Bot, um deinen Link zu erhalten.",
      btn_copy_ref: "📋 Kopieren", btn_share_ref: "📤 Teilen",
      error_title: "Etwas ist schiefgelaufen", error_msg: "Versuche das Dashboard erneut zu öffnen",
    },
    fr: {
      days: ["Di", "Lu", "Ma", "Me", "Je", "Ve", "Sa"],
      greet: "Bonjour",
      min_abbr: "min",
      level_1: "Déb.", level_2: "Base", level_3: "Moy.", level_4: "Bien", level_5: "Pro",
      diff_easy: "facile", diff_medium: "moyen", diff_hard: "difficile",
      err_name_empty: "Le nom ne peut pas être vide",
      err_name_long: "Max 30 caractères",
      err_goal_long: "Max 150 caractères",
      err_reminder_fmt: "Format : HH:MM — ex. 09:30",
      saving: "Enregistrement...",
      saved: "✓ Enregistré",
      save_error: "✗ Erreur — veuillez réessayer",
      lang_saved: "✓ Enregistré",
      lang_error: "✗ Erreur",
      day_abbr: "j.",
      milestones_done: "Toutes les récompenses jalons obtenues 🏆",
      progress_need: "Encore {n} pour {reward}",
      goal_reached: "Objectif atteint !",
      expires_prefix: "jusqu'au ",
      locale_code: "fr-FR",
      shop_training_title: "Pour l'entraînement",
      shop_training_desc: "Petites friandises pour l'apprentissage des commandes",
      shop_longplay_title: "Longue durée",
      shop_longplay_desc: "Friandises à mâcher pour le jeu autonome",
      shop_bysize_title: "Pour les petits",
      shop_bysize_desc: "Chiots et petites races — adaptés à la taille",
      shop_open_btn: "Ouvrir →",
      copy_ok: "✓ Lien copié",
      copy_fail: "✗ Impossible de copier",
      share_text: "Entraîne ton animal avec le coach IA Pepito ! 🐾",
      coach_load_error: "Impossible de charger les consultations. Réessayez plus tard.",
      thread_default_title: "Consultation",
      thread_active: "Actif",
      thread_archived: "Archivé",
      thread_click_active: "💬 Sujet «{title}» actif. Ouvrez le bot pour continuer.",
      thread_click_archived: "📁 Sujet «{title}» archivé. Démarrez une nouvelle consultation dans le bot.",
      thread_archive_btn: "🗂 Archiver",
      thread_archive_error: "Archivage impossible. Veuillez réessayer.",
      date_today: "aujourd'hui",
      date_yesterday: "hier",
      date_days_ago: "il y a {n} jours",
      date_locale: "fr-FR",
      msg_1: "message", msg_2: "messages", msg_many: "messages",
      stat_done_lbl: "faites", stat_done_sub: "aujourd'hui",
      stat_days_lbl: "séances", stat_days_sub: "total",
      card_progress_title: "Progrès du jour", card_training_title: "Entraînement aujourd'hui",
      no_plan_title: "Pas de plan pour aujourd'hui", no_plan_hint: "Ouvre le bot et crée un entraînement",
      all_done_title: "Toutes les tâches accomplies !", all_done_sub: "Super entraînement aujourd'hui",
      profile_heading: "✏️ Profil de l'animal", no_pet_title: "Profil incomplet",
      no_pet_hint: "Complète l'onboarding dans le bot pour remplir les données de ton animal",
      lbl_pet_name: "Nom de l'animal", lbl_breed: "Race", lbl_goal: "Objectif d'entraînement",
      lbl_level: "Niveau", lbl_age: "Âge", btn_save_pet: "Enregistrer les modifications",
      select_default: "— choisir —",
      age_1: "jusqu'à 4 mois", age_2: "4–12 mois", age_3: "1–3 ans", age_4: "3–7 ans", age_5: "7+ ans",
      settings_heading: "⚙️ Paramètres", card_notif_title: "Notifications",
      lbl_reminder: "Heure de rappel", hint_reminder_tz: "Heure locale — dans le fuseau horaire sélectionné ci-dessous",
      lbl_tz: "Fuseau horaire", btn_save_settings: "Enregistrer", card_lang_title: "Langue du bot",
      prem_hint_title: "Analyses avancées", prem_hint_sub: "Disponible en Premium",
      prem_hint_desc: "Analyse IA approfondie des progrès, recommandations personnalisées pour ton animal et statistiques détaillées.",
      btn_premium_hint: "En savoir plus dans le bot",
      rewards_heading: "🎁 Récompenses", card_invite_title: "Inviter un ami",
      ref_friends_lbl: "amis invités", how_works_title: "Comment ça marche",
      how_step_1: "Partage ton lien avec un ami",
      how_step_2: "L'ami s'inscrit et remplit le profil de l'animal",
      how_step_3: "Vous obtenez tous les deux {days} Premium gratuitement",
      how_step_4: "Invite davantage — gagne des bonus jalons !",
      prem_ben_1: "♾️ Entraîneur IA illimité", prem_ben_2: "🧠 Analyse approfondie des progrès",
      prem_ben_3: "🎥 Analyse vidéo et 🎤 vocale", prem_ben_4: "🎁 Recommandations de friandises personnalisées",
      btn_buy_premium: "⭐ Obtenir Premium", prem_active_lbl: "PREMIUM ACTIF",
      prem_expiry_warn: "⚠️ Expire bientôt — renouvelle dans le bot", card_shop_title: "Boutique de friandises",
      coach_heading: "💬 Consultations", coach_subheading: "Historique des séances avec l'entraîneur IA",
      coach_empty_title: "Pas encore de consultations",
      coach_empty_hint: "Pose des questions à l'entraîneur IA dans le bot — les sujets sont sauvegardés ici comme dossiers précieux",
      tab_lbl_pet: "Animal", tab_lbl_settings: "Paramètres",
      tab_lbl_rewards: "Récompenses", tab_lbl_coach: "Entraîneur",
      btn_retry: "Réessayer", loading_text: "Chargement...",
      ref_no_link: "Ouvre <b>🐾 Inviter un ami</b> dans le bot pour obtenir ton lien.",
      btn_copy_ref: "📋 Copier", btn_share_ref: "📤 Partager",
      error_title: "Quelque chose a mal tourné", error_msg: "Essaie d'ouvrir à nouveau le tableau de bord",
    },
    es: {
      days: ["Do", "Lu", "Ma", "Mi", "Ju", "Vi", "Sá"],
      greet: "Hola",
      min_abbr: "min",
      level_1: "Prin.", level_2: "Base", level_3: "Med.", level_4: "Buen", level_5: "Pro",
      diff_easy: "fácil", diff_medium: "medio", diff_hard: "difícil",
      err_name_empty: "El nombre no puede estar vacío",
      err_name_long: "Máx. 30 caracteres",
      err_goal_long: "Máx. 150 caracteres",
      err_reminder_fmt: "Formato: HH:MM — ej. 09:30",
      saving: "Guardando...",
      saved: "✓ Guardado",
      save_error: "✗ Error — inténtalo de nuevo",
      lang_saved: "✓ Guardado",
      lang_error: "✗ Error",
      day_abbr: "d.",
      milestones_done: "¡Todas las recompensas obtenidas! 🏆",
      progress_need: "{n} más para {reward}",
      goal_reached: "¡Meta alcanzada!",
      expires_prefix: "hasta ",
      locale_code: "es-ES",
      shop_training_title: "Para entrenar",
      shop_training_desc: "Premios pequeños para enseñar comandos",
      shop_longplay_title: "Larga duración",
      shop_longplay_desc: "Snacks masticables para juego autónomo",
      shop_bysize_title: "Para pequeños",
      shop_bysize_desc: "Cachorros y razas pequeñas — talla adecuada",
      shop_open_btn: "Abrir →",
      copy_ok: "✓ Enlace copiado",
      copy_fail: "✗ No se pudo copiar",
      share_text: "¡Entrena a tu mascota con el coach IA Pepito! 🐾",
      coach_load_error: "No se pudieron cargar las sesiones. Inténtalo más tarde.",
      thread_default_title: "Consulta",
      thread_active: "Activo",
      thread_archived: "Archivado",
      thread_click_active: "💬 Tema «{title}» activo. Abre el bot para continuar.",
      thread_click_archived: "📁 Tema «{title}» archivado. Inicia una nueva consulta en el bot.",
      thread_archive_btn: "🗂 Archivar",
      thread_archive_error: "No se pudo archivar. Inténtalo de nuevo.",
      date_today: "hoy",
      date_yesterday: "ayer",
      date_days_ago: "hace {n} días",
      date_locale: "es-ES",
      msg_1: "mensaje", msg_2: "mensajes", msg_many: "mensajes",
      stat_done_lbl: "realizadas", stat_done_sub: "hoy",
      stat_days_lbl: "sesiones", stat_days_sub: "total",
      card_progress_title: "Progreso del día", card_training_title: "Entrenamiento hoy",
      no_plan_title: "Sin plan para hoy", no_plan_hint: "Abre el bot y crea un entrenamiento",
      all_done_title: "¡Todas las tareas completadas!", all_done_sub: "Gran sesión de entrenamiento hoy",
      profile_heading: "✏️ Perfil de la mascota", no_pet_title: "Perfil incompleto",
      no_pet_hint: "Completa el onboarding en el bot para rellenar los datos de tu mascota",
      lbl_pet_name: "Nombre de la mascota", lbl_breed: "Raza", lbl_goal: "Objetivo del entrenamiento",
      lbl_level: "Nivel", lbl_age: "Edad", btn_save_pet: "Guardar cambios",
      select_default: "— selecciona —",
      age_1: "hasta 4 meses", age_2: "4–12 meses", age_3: "1–3 años", age_4: "3–7 años", age_5: "7+ años",
      settings_heading: "⚙️ Configuración", card_notif_title: "Notificaciones",
      lbl_reminder: "Hora del recordatorio", hint_reminder_tz: "Hora local — en la zona horaria seleccionada abajo",
      lbl_tz: "Zona horaria", btn_save_settings: "Guardar", card_lang_title: "Idioma del bot",
      prem_hint_title: "Análisis avanzado", prem_hint_sub: "Disponible en Premium",
      prem_hint_desc: "Análisis IA profundo del progreso, recomendaciones personalizadas para tu mascota y estadísticas detalladas.",
      btn_premium_hint: "Saber más en el bot",
      rewards_heading: "🎁 Premios", card_invite_title: "Invitar a un amigo",
      ref_friends_lbl: "amigos invitados", how_works_title: "Cómo funciona",
      how_step_1: "Comparte tu enlace con un amigo",
      how_step_2: "El amigo se registra y completa el perfil de la mascota",
      how_step_3: "Ambos obtenéis {days} Premium gratis",
      how_step_4: "¡Invita más — gana bonos por hitos!",
      prem_ben_1: "♾️ Entrenador IA ilimitado", prem_ben_2: "🧠 Análisis profundo del progreso",
      prem_ben_3: "🎥 Análisis de vídeo y 🎤 voz", prem_ben_4: "🎁 Recomendaciones personalizadas de premios",
      btn_buy_premium: "⭐ Obtener Premium", prem_active_lbl: "PREMIUM ACTIVO",
      prem_expiry_warn: "⚠️ Vence pronto — renueva en el bot", card_shop_title: "Tienda de premios",
      coach_heading: "💬 Consultas", coach_subheading: "Historial de sesiones con el entrenador IA",
      coach_empty_title: "Sin consultas aún",
      coach_empty_hint: "Pregunta al entrenador IA en el bot — los temas se guardan aquí como registros valiosos",
      tab_lbl_pet: "Mascota", tab_lbl_settings: "Configuración",
      tab_lbl_rewards: "Premios", tab_lbl_coach: "Entrenador",
      btn_retry: "Intentar de nuevo", loading_text: "Cargando...",
      ref_no_link: "Abre <b>🐾 Invitar a un amigo</b> en el bot para obtener tu enlace.",
      btn_copy_ref: "📋 Copiar", btn_share_ref: "📤 Compartir",
      error_title: "Algo salió mal", error_msg: "Intenta abrir el panel de nuevo",
    },
    pt: {
      days: ["Do", "Se", "Te", "Qu", "Qi", "Sx", "Sá"],
      greet: "Olá",
      min_abbr: "min",
      level_1: "Init.", level_2: "Base", level_3: "Méd.", level_4: "Bom", level_5: "Prof.",
      diff_easy: "fácil", diff_medium: "médio", diff_hard: "difícil",
      err_name_empty: "O nome não pode estar vazio",
      err_name_long: "Máx. 30 caracteres",
      err_goal_long: "Máx. 150 caracteres",
      err_reminder_fmt: "Formato: HH:MM — ex. 09:30",
      saving: "Salvando...",
      saved: "✓ Salvo",
      save_error: "✗ Erro — tente novamente",
      lang_saved: "✓ Salvo",
      lang_error: "✗ Erro",
      day_abbr: "d.",
      milestones_done: "Todas as recompensas obtidas 🏆",
      progress_need: "Mais {n} para {reward}",
      goal_reached: "Meta atingida!",
      expires_prefix: "até ",
      locale_code: "pt-BR",
      shop_training_title: "Para treino",
      shop_training_desc: "Petiscos pequenos para ensinar comandos",
      shop_longplay_title: "Longa duração",
      shop_longplay_desc: "Petiscos mastigáveis para brincar sozinho",
      shop_bysize_title: "Para pequenos",
      shop_bysize_desc: "Filhotes e raças pequenas — tamanho adequado",
      shop_open_btn: "Abrir →",
      copy_ok: "✓ Link copiado",
      copy_fail: "✗ Não foi possível copiar",
      share_text: "Treine seu pet com o coach IA Pepito! 🐾",
      coach_load_error: "Não foi possível carregar as sessões. Tente mais tarde.",
      thread_default_title: "Consulta",
      thread_active: "Ativo",
      thread_archived: "Arquivado",
      thread_click_active: "💬 Tópico «{title}» ativo. Abra o bot para continuar.",
      thread_click_archived: "📁 Tópico «{title}» arquivado. Inicie uma nova consulta no bot.",
      thread_archive_btn: "🗂 Arquivar",
      thread_archive_error: "Não foi possível arquivar. Tente novamente.",
      date_today: "hoje",
      date_yesterday: "ontem",
      date_days_ago: "há {n} dias",
      date_locale: "pt-BR",
      msg_1: "mensagem", msg_2: "mensagens", msg_many: "mensagens",
      stat_done_lbl: "realizadas", stat_done_sub: "hoje",
      stat_days_lbl: "sessões", stat_days_sub: "total",
      card_progress_title: "Progresso do dia", card_training_title: "Treino hoje",
      no_plan_title: "Sem plano para hoje", no_plan_hint: "Abra o bot para criar um treino",
      all_done_title: "Todas as tarefas concluídas!", all_done_sub: "Ótima sessão de treino hoje",
      profile_heading: "✏️ Perfil do pet", no_pet_title: "Perfil incompleto",
      no_pet_hint: "Complete o onboarding no bot para preencher os dados do pet",
      lbl_pet_name: "Nome do pet", lbl_breed: "Raça", lbl_goal: "Objetivo do treino",
      lbl_level: "Nível", lbl_age: "Idade", btn_save_pet: "Salvar alterações",
      select_default: "— selecionar —",
      age_1: "até 4 meses", age_2: "4–12 meses", age_3: "1–3 anos", age_4: "3–7 anos", age_5: "7+ anos",
      settings_heading: "⚙️ Configurações", card_notif_title: "Notificações",
      lbl_reminder: "Hora do lembrete", hint_reminder_tz: "Hora local — no fuso horário selecionado abaixo",
      lbl_tz: "Fuso horário", btn_save_settings: "Salvar", card_lang_title: "Idioma do bot",
      prem_hint_title: "Análise avançada", prem_hint_sub: "Disponível no Premium",
      prem_hint_desc: "Análise IA aprofundada do progresso, recomendações personalizadas para o seu pet e estatísticas detalhadas.",
      btn_premium_hint: "Saber mais no bot",
      rewards_heading: "🎁 Recompensas", card_invite_title: "Convidar um amigo",
      ref_friends_lbl: "amigos convidados", how_works_title: "Como funciona",
      how_step_1: "Compartilhe seu link com um amigo",
      how_step_2: "O amigo se registra e preenche o perfil do pet",
      how_step_3: "Vocês dois recebem {days} Premium grátis",
      how_step_4: "Convide mais — ganhe bônus por marcos!",
      prem_ben_1: "♾️ Treinador IA ilimitado", prem_ben_2: "🧠 Análise aprofundada do progresso",
      prem_ben_3: "🎥 Análise de vídeo e 🎤 voz", prem_ben_4: "🎁 Recomendações personalizadas de petiscos",
      btn_buy_premium: "⭐ Obter Premium", prem_active_lbl: "PREMIUM ATIVO",
      prem_expiry_warn: "⚠️ Vence em breve — renove no bot", card_shop_title: "Loja de petiscos",
      coach_heading: "💬 Consultas", coach_subheading: "Histórico de sessões com o treinador IA",
      coach_empty_title: "Sem consultas ainda",
      coach_empty_hint: "Faça perguntas ao treinador IA no bot — os tópicos são salvos aqui como registros valiosos",
      tab_lbl_pet: "Pet", tab_lbl_settings: "Configurações",
      tab_lbl_rewards: "Recompensas", tab_lbl_coach: "Treinador",
      btn_retry: "Tentar novamente", loading_text: "Carregando...",
      ref_no_link: "Abra <b>🐾 Convidar um amigo</b> no bot para obter seu link.",
      btn_copy_ref: "📋 Copiar", btn_share_ref: "📤 Compartilhar",
      error_title: "Algo deu errado", error_msg: "Tente abrir o painel novamente",
    },
  };

  let _lang = "ru";

  function _norm_lang(code) {
    if (!code) return "ru";
    const base = String(code).split("-")[0].toLowerCase();
    return WEBAPP_I18N[base] ? base : "ru";
  }

  function _ui(key, repl) {
    const dict = WEBAPP_I18N[_lang] || WEBAPP_I18N.ru;
    let s = dict[key] !== undefined ? dict[key] : (WEBAPP_I18N.ru[key] || key);
    if (repl) Object.keys(repl).forEach(k => { s = s.split("{" + k + "}").join(repl[k]); });
    return s;
  }

  // ── applyI18n: update all static HTML text to current _lang ────────
  function applyI18n() {
    const setText = (id, key) => { const e = $(id); if (e) e.textContent = _ui(key); };
    const setHTML = (id, key) => { const e = $(id); if (e) e.innerHTML = _ui(key); };

    // Loading / error
    setText("loading-text", "loading_text");
    setText("btn-retry", "btn_retry");

    // Tab bar
    setText("tab-lbl-pet", "tab_lbl_pet");
    setText("tab-lbl-settings", "tab_lbl_settings");
    setText("tab-lbl-rewards", "tab_lbl_rewards");
    setText("tab-lbl-coach", "tab_lbl_coach");

    // Hero / stats
    const heroLabel = $("hero-label");
    if (heroLabel) heroLabel.textContent = _ui("greet") + ",";
    setText("stat-done-lbl", "stat_done_lbl");
    setText("stat-done-sub", "stat_done_sub");
    setText("stat-days-lbl", "stat_days_lbl");
    setText("stat-days-sub", "stat_days_sub");

    // Progress card
    setText("card-progress-title", "card_progress_title");
    setText("card-training-title", "card_training_title");

    // No-plan / all-done
    setText("no-plan-title", "no_plan_title");
    setText("no-plan-hint", "no_plan_hint");
    setText("all-done-title", "all_done_title");
    setText("all-done-sub", "all_done_sub");

    // Profile section
    setText("profile-heading", "profile_heading");
    setText("no-pet-title", "no_pet_title");
    setText("no-pet-hint", "no_pet_hint");
    setText("lbl-pet-name", "lbl_pet_name");
    setText("lbl-breed", "lbl_breed");
    setText("lbl-goal", "lbl_goal");
    setText("lbl-level", "lbl_level");
    setText("lbl-age", "lbl_age");
    const savePetBtn = $("btn-save-pet");
    if (savePetBtn) { savePetBtn.textContent = _ui("btn_save_pet"); savePetBtn.dataset.label = _ui("btn_save_pet"); }

    // Level select options (values stay as "1"-"5", only labels translate)
    const levelSel = $("pf-level");
    if (levelSel) {
      const opts = levelSel.options;
      if (opts.length >= 1) opts[0].text = _ui("select_default");
      for (let i = 1; i <= 5; i++) { if (opts[i]) opts[i].text = i + " — " + _ui("level_" + i); }
    }

    // Age select options (values are stored Russian strings — labels only translate)
    const ageSel = $("pf-age");
    if (ageSel) {
      const opts = ageSel.options;
      if (opts.length >= 1) opts[0].text = _ui("select_default");
      const ageKeys = ["age_1","age_2","age_3","age_4","age_5"];
      for (let i = 0; i < ageKeys.length; i++) { if (opts[i+1]) opts[i+1].text = _ui(ageKeys[i]); }
    }

    // Settings tab
    setText("settings-heading", "settings_heading");
    setText("card-notif-title", "card_notif_title");
    setText("lbl-reminder", "lbl_reminder");
    setText("hint-reminder-tz", "hint_reminder_tz");
    setText("lbl-tz", "lbl_tz");
    const saveSetBtn = $("btn-save-settings");
    if (saveSetBtn) { saveSetBtn.textContent = _ui("btn_save_settings"); saveSetBtn.dataset.label = _ui("btn_save_settings"); }
    setText("card-lang-title", "card_lang_title");
    setText("prem-hint-title", "prem_hint_title");
    setText("prem-hint-sub", "prem_hint_sub");
    setText("prem-hint-desc", "prem_hint_desc");
    setText("btn-premium-hint", "btn_premium_hint");

    // Rewards tab
    setText("rewards-heading", "rewards_heading");
    setText("card-invite-title", "card_invite_title");
    setText("ref-friends-lbl", "ref_friends_lbl");
    setText("how-works-title", "how_works_title");
    setText("how-step-1", "how_step_1");
    setText("how-step-2", "how_step_2");
    setText("how-step-4", "how_step_4");
    setText("prem-ben-1", "prem_ben_1");
    setText("prem-ben-2", "prem_ben_2");
    setText("prem-ben-3", "prem_ben_3");
    setText("prem-ben-4", "prem_ben_4");
    const buyBtn = $("btn-buy-premium");
    if (buyBtn) buyBtn.textContent = _ui("btn_buy_premium");
    setText("prem-active-lbl", "prem_active_lbl");
    setText("prem-expiry-warn", "prem_expiry_warn");
    setText("card-shop-title", "card_shop_title");

    // Ref no-link (has HTML markup)
    setHTML("ref-no-link", "ref_no_link");

    // Ref copy/share buttons
    setText("btn-copy-ref", "btn_copy_ref");
    setText("btn-share-ref", "btn_share_ref");

    // how-step-3: uses bonus days from _data if available, otherwise fallback
    const step3El = $("how-step-3");
    if (step3El) {
      const bonusDays = (_data && _data.growth && _data.growth.base_bonus_days) || 3;
      step3El.textContent = _ui("how_step_3", { days: "+" + bonusDays + " " + _ui("day_abbr") });
    }

    // Error screen
    setText("error-title", "error_title");
    setText("error-msg", "error_msg");

    // Coach tab
    setText("coach-heading", "coach_heading");
    setText("coach-subheading", "coach_subheading");
    setText("coach-empty-title", "coach_empty_title");
    setText("coach-empty-hint", "coach_empty_hint");
  }

  // ── State ──────────────────────────────────────────────────────────
  let _data = null;
  const initData = tg.initData;
  const TODAY_STR = new Date().toISOString().slice(0, 10);

  // ── DOM helpers ────────────────────────────────────────────────────
  const $ = id => document.getElementById(id);
  const show = id => { const e = $(id); if (e) e.classList.remove("hidden"); };
  const hide = id => { const e = $(id); if (e) e.classList.add("hidden"); };
  const val  = id => { const e = $(id); return e ? e.value : ""; };

  // ── API ────────────────────────────────────────────────────────────
  async function trackEvent(event) {
    try {
      await apiFetch("/api/metrics/event", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event }),
      });
    } catch (_) {}
  }

  async function apiFetch(path, opts = {}) {
    const res = await fetch(path, {
      ...opts,
      headers: { "X-Telegram-Init-Data": initData, ...(opts.headers || {}) },
    });
    if (!res.ok) {
      const err = new Error("HTTP " + res.status);
      err.status = res.status;
      if (res.status === 422) {
        try { err.data = await res.json(); } catch (_) {}
      }
      throw err;
    }
    return res.json();
  }

  // ── Load ───────────────────────────────────────────────────────────
  async function load() {
    hide("state-error");
    hide("tabs-container");
    hide("tab-bar");
    show("state-loading");

    try {
      _data = await apiFetch("/api/dashboard");
    } catch (e) {
      hide("state-loading");
      renderError(e.status);
      return;
    }

    _lang = _norm_lang(_data.settings?.language_code);
    applyI18n();
    hide("state-loading");
    renderDashboard(_data);
    if (_data.is_admin === true) renderAdminTab(_data.admin_stats);
    show("tabs-container");
    show("tab-bar");
    switchTab("pet");
  }

  function renderError(status) {
    if (status === 401) {
      $("error-title").textContent = "Session expired · Сессия истекла";
      $("error-msg").textContent = "Close the dashboard and reopen it from the bot. / Закрой и открой снова из бота.";
    } else if (status === 404) {
      $("error-title").textContent = "Account not found · Аккаунт не найден";
      $("error-msg").textContent = "Complete onboarding in the bot first. / Пройди онбординг в боте.";
    } else {
      $("error-title").textContent = "Connection error · Нет соединения";
      $("error-msg").textContent = "Check your internet and try again. / Проверь интернет.";
    }
    show("state-error");
  }

  $("btn-retry").addEventListener("click", load);

  // ── Tab navigation ─────────────────────────────────────────────────
  let TABS = ["pet", "settings", "rewards", "coach"];

  function switchTab(name) {
    TABS.forEach(t => {
      const btn = document.querySelector(`.tab[data-tab="${t}"]`);
      const panel = $("tab-" + t);
      if (btn)   btn.classList.toggle("tab--active", t === name);
      if (panel) panel.classList.toggle("hidden", t !== name);
    });

    if (name === "pet"      && _data) fillProfileForm();
    if (name === "settings" && _data) fillSettingsForm();
    if (name === "rewards"  && _data) renderRewards();
    if (name === "coach")            fetchAndRenderCoach();
  }

  document.querySelectorAll(".tab[data-tab]").forEach(btn => {
    btn.addEventListener("click", () => switchTab(btn.dataset.tab));
  });

  // ── Dashboard render ───────────────────────────────────────────────
  function renderDashboard(data) {
    const { user, pet, today_tasks, weekly_progress } = data;

    $("hero-user-name").textContent = user.first_name || _ui("greet");
    if (user.is_premium) show("premium-badge");

    if (pet) {
      show("pet-hero");
      $("pet-hero-name").textContent = pet.name;
      updateHeroMeta(pet);
    }

    if (weekly_progress.training_days > 0) {
      show("streak-chip");
      $("streak-value").textContent = weekly_progress.training_days;
    }

    $("stat-done").textContent = weekly_progress.completed_tasks;
    $("stat-days").textContent = weekly_progress.training_days;

    syncProgress(weekly_progress.completed_tasks, weekly_progress.total_tasks);
    renderChart(weekly_progress.weekly_chart || []);
    renderTasks(today_tasks);
  }

  function updateHeroMeta(pet) {
    if (!pet) return;
    const meta = [];
    if (pet.breed)          meta.push(pet.breed);
    if (pet.training_level) meta.push(levelLabel(pet.training_level));
    if (pet.age_category)   meta.push(pet.age_category);
    const el = $("pet-hero-meta");
    if (el) el.textContent = meta.join(" · ") || "";
  }

  // ── Progress ───────────────────────────────────────────────────────
  function syncProgress(done, total) {
    const pct = total > 0 ? Math.round((done / total) * 100) : 0;
    $("progress-fraction").textContent = done + " / " + total;
    requestAnimationFrame(() => { $("progress-fill").style.width = pct + "%"; });
    const badge = $("tasks-badge");
    if (badge) badge.textContent = done + "/" + total;
    $("stat-done").textContent = done;
  }

  // ── Week chart ─────────────────────────────────────────────────────
  function renderChart(chart) {
    const container = $("week-chart");
    if (!container) return;
    container.innerHTML = "";
    const maxVal = Math.max(...chart.map(d => d.completed), 1);

    chart.forEach(day => {
      const isToday = day.date === TODAY_STR;
      const pct = Math.round((day.completed / maxVal) * 100);
      const d = new Date(day.date + "T12:00:00");

      const col  = document.createElement("div");
      col.className = "chart-col";
      if (isToday) col.dataset.today = "1";

      const wrap = document.createElement("div");
      wrap.className = "chart-bar-wrap";

      const fill = document.createElement("div");
      fill.className = "chart-bar-fill" + (isToday ? " chart-bar-fill--today" : "");
      wrap.appendChild(fill);

      const label = document.createElement("div");
      label.className = "chart-label" + (isToday ? " chart-label--today" : "");
      label.textContent = _ui("days")[d.getDay()];

      col.appendChild(wrap);
      col.appendChild(label);
      container.appendChild(col);
      requestAnimationFrame(() => { fill.style.height = pct + "%"; });
    });
  }

  // ── Tasks ──────────────────────────────────────────────────────────
  function renderTasks(tasks) {
    const list = $("tasks-list");
    list.innerHTML = "";
    hide("state-no-plan");
    hide("state-all-done");

    if (tasks.length === 0) { show("state-no-plan"); return; }

    tasks.forEach(task => list.appendChild(buildTaskEl(task)));
    if (tasks.every(t => t.is_completed)) show("state-all-done");
  }

  function buildTaskEl(task) {
    const el = document.createElement("div");
    el.className = "task-item";
    el.dataset.id = task.id;

    const chips = [];
    if (task.duration_minutes) chips.push("⏱ " + task.duration_minutes + " " + _ui("min_abbr"));
    if (task.difficulty)       chips.push(diffLabel(task.difficulty));

    el.innerHTML =
      '<div class="task-checkbox' + (task.is_completed ? " task-checkbox--done" : "") + '">' +
        '<span class="task-check-icon">✓</span>' +
      "</div>" +
      '<div class="task-body">' +
        '<div class="task-title' + (task.is_completed ? " task-title--done" : "") + '">' +
          escHtml(task.title) +
        "</div>" +
        (chips.length
          ? '<div class="task-meta">' +
              chips.map(c => '<span class="task-chip">' + escHtml(c) + "</span>").join("") +
            "</div>"
          : "") +
      "</div>";

    el.addEventListener("click", () => onToggle(task, el));
    return el;
  }

  async function onToggle(task, el) {
    if (el.classList.contains("task-item--pending")) return;
    const prev = task.is_completed;
    task.is_completed = !prev;
    applyCheckbox(task.is_completed, el);
    el.classList.add("task-item--pending");
    updateTaskProgress();
    try { tg.HapticFeedback.impactOccurred("light"); } catch (_) {}

    try {
      const res = await apiFetch("/api/tasks/" + task.id + "/toggle", { method: "POST" });
      task.is_completed = res.is_completed;
      applyCheckbox(task.is_completed, el);
      updateTaskProgress();
      if (res.plan_completed) {
        show("state-all-done");
        try { tg.HapticFeedback.notificationOccurred("success"); } catch (_) {}
      } else {
        hide("state-all-done");
      }
    } catch (_) {
      task.is_completed = prev;
      applyCheckbox(prev, el);
      updateTaskProgress();
    } finally {
      el.classList.remove("task-item--pending");
    }
  }

  function applyCheckbox(done, el) {
    el.querySelector(".task-checkbox").classList.toggle("task-checkbox--done", done);
    el.querySelector(".task-title").classList.toggle("task-title--done", done);
  }

  function updateTaskProgress() {
    if (!_data) return;
    const tasks = _data.today_tasks;
    syncProgress(tasks.filter(t => t.is_completed).length, tasks.length);
  }

  // ── Profile form ───────────────────────────────────────────────────
  function fillProfileForm() {
    const pet = _data && _data.pet;
    if (!pet) {
      show("profile-no-pet");
      hide("profile-form-wrap");
      return;
    }
    hide("profile-no-pet");
    show("profile-form-wrap");

    $("pf-name").value  = pet.name || "";
    $("pf-breed").value = pet.breed || "";
    $("pf-goal").value  = pet.goal || "";
    setSelectVal("pf-level", pet.training_level || "");
    setSelectVal("pf-age", pet.age_category || "");
    clearFieldErrors(["err-name", "err-goal"]);
  }

  $("btn-save-pet").addEventListener("click", async () => {
    clearFieldErrors(["err-name", "err-goal"]);

    const name = val("pf-name").trim();
    if (!name) { setFieldError("err-name", _ui("err_name_empty")); return; }
    if (name.length > 30) { setFieldError("err-name", _ui("err_name_long")); return; }
    const goal = val("pf-goal").trim();
    if (goal.length > 150) { setFieldError("err-goal", _ui("err_goal_long")); return; }

    const body = {
      name,
      breed: val("pf-breed").trim(),
      goal,
      training_level: val("pf-level") || null,
      age_category:   val("pf-age")   || null,
    };

    await saveWithFeedback("btn-save-pet", "save-pet-status", async () => {
      let res;
      try {
        res = await apiFetch("/api/profile/pet", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
      } catch (e) {
        if (e.status === 422 && e.data && e.data.errors) {
          e.data.errors.forEach(err => {
            const errId = { name: "err-name", goal: "err-goal" }[err.field];
            if (errId) setFieldError(errId, err.msg);
          });
        }
        throw e;
      }

      if (_data) {
        _data.pet = Object.assign(_data.pet || {}, res.pet);
        $("pet-hero-name").textContent = res.pet.name;
        updateHeroMeta(res.pet);
        if ($("pet-hero").classList.contains("hidden")) show("pet-hero");
      }
      try { tg.HapticFeedback.notificationOccurred("success"); } catch (_) {}
    });
  });

  // ── Settings form ──────────────────────────────────────────────────
  function fillSettingsForm() {
    const s = (_data && _data.settings) || {};
    $("st-reminder").value = s.reminder_time || "";
    setSelectVal("st-tz", s.timezone || "UTC");
    setActiveLang(s.language_code || "ru");

    if (_data && _data.user && !_data.user.is_premium) {
      show("premium-hint-card");
    }
    clearFieldErrors(["err-reminder"]);
  }

  $("btn-save-settings").addEventListener("click", async () => {
    clearFieldErrors(["err-reminder"]);

    const rt = val("st-reminder").trim();
    if (rt && !/^([01]\d|2[0-3]):[0-5]\d$/.test(rt)) {
      setFieldError("err-reminder", _ui("err_reminder_fmt"));
      return;
    }

    const body = {
      reminder_time: rt || null,
      timezone:      val("st-tz"),
    };

    await saveWithFeedback("btn-save-settings", "save-settings-status", async () => {
      try {
        await apiFetch("/api/profile/settings", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
      } catch (e) {
        if (e.status === 422 && e.data && e.data.errors) {
          e.data.errors.forEach(err => {
            if (err.field === "reminder_time") setFieldError("err-reminder", err.msg);
          });
        }
        throw e;
      }
      if (_data && _data.settings) {
        _data.settings.reminder_time = body.reminder_time;
        _data.settings.timezone      = body.timezone;
      }
      try { tg.HapticFeedback.notificationOccurred("success"); } catch (_) {}
    });
  });

  document.querySelectorAll(".lang-chip[data-lang]").forEach(chip => {
    chip.addEventListener("click", async () => {
      const lang = chip.dataset.lang;
      setActiveLang(lang);
      const statusEl = $("save-lang-status");
      statusEl.textContent = "";
      statusEl.className = "save-status";
      try {
        await apiFetch("/api/profile/settings", {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ language_code: lang }),
        });
        if (_data && _data.settings) _data.settings.language_code = lang;
        _lang = _norm_lang(lang);
        applyI18n();
        statusEl.textContent = _ui("lang_saved");
        statusEl.className = "save-status save-status--ok";
        setTimeout(() => { statusEl.textContent = ""; }, 2000);
        try { tg.HapticFeedback.impactOccurred("light"); } catch (_) {}
      } catch (_) {
        statusEl.textContent = _ui("lang_error");
        statusEl.className = "save-status save-status--err";
        setTimeout(() => { statusEl.textContent = ""; }, 2500);
      }
    });
  });

  function setActiveLang(lang) {
    document.querySelectorAll(".lang-chip[data-lang]").forEach(c => {
      c.classList.toggle("lang-chip--active", c.dataset.lang === lang);
    });
  }

  $("btn-premium-hint").addEventListener("click", () => {
    try { tg.close(); } catch (_) {}
  });

  // ── Rewards tab ────────────────────────────────────────────────────
  function renderRewards() {
    if (!_data) return;
    const { user, growth } = _data;
    if (!growth) return;

    // Referral counter
    $("ref-count").textContent = growth.referral_count;
    renderMilestoneTrack(growth.milestones, growth.referral_count, growth.base_bonus_days);
    renderProgressHint(growth);

    // Sync "how it works" bonus text with the same API source as milestone-track
    const bonusDays = growth.base_bonus_days || 3;
    const step3El = $("how-step-3");
    if (step3El) {
      step3El.textContent = _ui("how_step_3", { days: "+" + bonusDays + " " + _ui("day_abbr") });
    }

    if (growth.referral_link) {
      $("ref-link-text").textContent = growth.referral_link;
      show("ref-link-wrap");
      hide("ref-no-link");
    } else {
      hide("ref-link-wrap");
      show("ref-no-link");
    }

    // Premium card
    if (user.is_premium && user.subscription_expires_at) {
      hide("premium-upsell-card");
      show("premium-active-card");
      renderPremiumActive(user.subscription_expires_at);
    } else {
      show("premium-upsell-card");
      hide("premium-active-card");
    }

    // Shop cards
    renderShopCards(growth.shop_urls);
  }

  function renderMilestoneTrack(milestones, count, baseBonusDays) {
    const track = $("milestone-track");
    if (!track || !milestones) return;
    track.innerHTML = "";

    const base = { count: 1, reward: "+" + (baseBonusDays || 3) + " " + _ui("day_abbr"), achieved: count >= 1 };
    const allTiers = [base, ...milestones];

    allTiers.forEach((m, i) => {
      const achieved = m.achieved;
      const isNext = !achieved && (i === 0 || allTiers[i - 1].achieved);

      if (i > 0) {
        const conn = document.createElement("div");
        conn.className = "milestone-conn" + (allTiers[i - 1].achieved ? " milestone-conn--done" : "");
        track.appendChild(conn);
      }

      const node = document.createElement("div");
      node.className = "milestone-node" +
        (achieved ? " milestone-node--done" : isNext ? " milestone-node--next" : "");

      const bubble = document.createElement("div");
      bubble.className = "milestone-bubble";
      bubble.textContent = m.count;

      const rewardLbl = document.createElement("div");
      rewardLbl.className = "milestone-reward";
      rewardLbl.textContent = m.reward;

      node.appendChild(bubble);
      node.appendChild(rewardLbl);
      track.appendChild(node);
    });
  }

  function renderProgressHint(growth) {
    const el = $("ref-progress-hint");
    if (!el) return;
    const nextTier = (growth.milestones || []).find(m => !m.achieved);
    if (!nextTier) {
      el.textContent = (growth.referral_count || 0) > 0 ? _ui("milestones_done") : "";
      return;
    }
    const needed = nextTier.count - (growth.referral_count || 0);
    el.textContent = needed > 0 ? _ui("progress_need", {n: needed, reward: nextTier.reward}) : _ui("goal_reached");
  }

  function renderPremiumActive(expiresAt) {
    const expires = new Date(expiresAt);
    const now     = new Date();
    const msLeft  = expires - now;
    const daysLeft = Math.ceil(msLeft / (1000 * 60 * 60 * 24));

    const dateStr = expires.toLocaleDateString(_ui("locale_code"), {
      day: "numeric", month: "long", year: "numeric",
    });
    $("prem-expires-text").textContent = _ui("expires_prefix") + dateStr;

    const pct = Math.max(0, Math.min(100, Math.round((daysLeft / 30) * 100)));
    requestAnimationFrame(() => { $("prem-bar-fill").style.width = pct + "%"; });

    if (daysLeft <= 7) show("prem-expiry-warn");
  }

  function renderShopCards(shopUrls) {
    const container = $("shop-cards");
    if (!container || !shopUrls) return;

    const cards = [
      {
        emoji: "🦴",
        title: _ui("shop_training_title"),
        desc:  _ui("shop_training_desc"),
        url:   shopUrls.training,
      },
      {
        emoji: "🎁",
        title: _ui("shop_longplay_title"),
        desc:  _ui("shop_longplay_desc"),
        url:   shopUrls.longplay,
      },
      {
        emoji: "🐶",
        title: _ui("shop_bysize_title"),
        desc:  _ui("shop_bysize_desc"),
        url:   shopUrls.by_size,
      },
    ];

    container.innerHTML = "";
    cards.forEach(card => {
      const el = document.createElement("div");
      el.className = "shop-card";
      el.innerHTML =
        '<div class="shop-card-emoji">' + card.emoji + "</div>" +
        '<div class="shop-card-title">' + escHtml(card.title) + "</div>" +
        '<div class="shop-card-desc">'  + escHtml(card.desc)  + "</div>" +
        '<button class="shop-card-btn">' + escHtml(_ui("shop_open_btn")) + '</button>';
      el.querySelector(".shop-card-btn").addEventListener("click", () => {
        try { tg.openLink(card.url); } catch (_) { window.open(card.url, "_blank"); }
      });
      container.appendChild(el);
    });
  }

  // ── Referral copy / share ──────────────────────────────────────────
  $("btn-copy-ref").addEventListener("click", async () => {
    const link     = $("ref-link-text").textContent;
    const statusEl = $("ref-copy-status");
    try {
      await navigator.clipboard.writeText(link);
      trackEvent("copy_click");
      statusEl.textContent = _ui("copy_ok");
      statusEl.className   = "save-status save-status--ok";
      try { tg.HapticFeedback.impactOccurred("light"); } catch (_) {}
      setTimeout(() => { statusEl.textContent = ""; }, 2500);
    } catch (_) {
      statusEl.textContent = _ui("copy_fail");
      statusEl.className   = "save-status save-status--err";
      setTimeout(() => { statusEl.textContent = ""; }, 2500);
    }
  });

  $("btn-share-ref").addEventListener("click", () => {
    const link = $("ref-link-text").textContent;
    const text = encodeURIComponent(_ui("share_text"));
    trackEvent("share_click");
    try {
      tg.openTelegramLink(
        "https://t.me/share/url?url=" + encodeURIComponent(link) + "&text=" + text
      );
    } catch (_) {}
  });

  // ── Premium CTA ────────────────────────────────────────────────────
  $("btn-buy-premium").addEventListener("click", () => {
    try { tg.sendData(JSON.stringify({ action: "buy_premium" })); } catch (_) {}
  });

  // ── Save wrapper ───────────────────────────────────────────────────
  async function saveWithFeedback(btnId, statusId, fn) {
    const btn    = $(btnId);
    const status = $(statusId);
    const label  = btn.dataset.label || _ui("saved").replace("✓ ", "");

    btn.disabled    = true;
    btn.textContent = _ui("saving");
    status.textContent = "";
    status.className   = "save-status";

    try {
      await fn();
      status.textContent = _ui("saved");
      status.className   = "save-status save-status--ok";
      setTimeout(() => { if (status.textContent === _ui("saved")) status.textContent = ""; }, 2500);
    } catch (_) {
      const hasInline = document.querySelectorAll(".field-error:not(:empty)").length > 0;
      if (!hasInline) {
        status.textContent = _ui("save_error");
        status.className   = "save-status save-status--err";
      }
    } finally {
      btn.disabled    = false;
      btn.textContent = label;
    }
  }

  // ── Form helpers ───────────────────────────────────────────────────
  function setSelectVal(id, value) {
    const el = $(id);
    if (!el) return;
    for (let i = 0; i < el.options.length; i++) {
      if (el.options[i].value === value) { el.selectedIndex = i; return; }
    }
    el.selectedIndex = 0;
  }

  function setFieldError(id, msg) {
    const el = $(id);
    if (el) el.textContent = msg;
  }

  function clearFieldErrors(ids) {
    ids.forEach(id => { const e = $(id); if (e) e.textContent = ""; });
  }

  // ── Labels ─────────────────────────────────────────────────────────
  function levelLabel(l) {
    return { "1": _ui("level_1"), "2": _ui("level_2"), "3": _ui("level_3"), "4": _ui("level_4"), "5": _ui("level_5") }[l] || l;
  }

  function diffLabel(d) {
    return { easy: _ui("diff_easy"), medium: _ui("diff_medium"), hard: _ui("diff_hard") }[d] || d;
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }

  // ── Admin tab (founder-only, injected after is_admin === true) ────
  function renderAdminTab(stats) {
    TABS.push("admin");

    const btn = document.createElement("button");
    btn.className = "tab";
    btn.dataset.tab = "admin";
    btn.innerHTML =
      '<span class="tab-icon">👑</span>' +
      '<span class="tab-label">Админка</span>';
    $("tab-bar").appendChild(btn);
    btn.addEventListener("click", () => switchTab("admin"));

    const s = stats || {};

    function buildCards(items) {
      return items.map(m =>
        '<div class="adm-card">' +
          '<div class="adm-card-icon">' + m.icon + '</div>' +
          '<div class="adm-card-value">' + m.value + '</div>' +
          '<div class="adm-card-label">' + escHtml(m.label) + '</div>' +
        '</div>'
      ).join("");
    }

    const userCards = buildCards([
      { icon: "👥", value: s.total_users    || 0, label: "Всего юзеров" },
      { icon: "⭐", value: s.premium_users  || 0, label: "Premium" },
      { icon: "🔗", value: s.referrals_given || 0, label: "Рефералов" },
    ]);

    const todayCards = buildCards([
      { icon: "🆕", value: s.new_today      || 0, label: "Новых сегодня" },
      { icon: "🔥", value: s.active_today   || 0, label: "Активных сегодня" },
      { icon: "📈", value: (s.conversion_pct || 0) + "%", label: "Конверсия →Premium" },
    ]);

    const vaCards = buildCards([
      { icon: "✅", value: s.va_mark_done    || 0, label: "Задач отмечено" },
      { icon: "🔒", value: s.va_premium_gate || 0, label: "Premium gate" },
      { icon: "⚠️", value: s.va_fallback     || 0, label: "AI fallback" },
    ]);

    const panel = document.createElement("div");
    panel.id = "tab-admin";
    panel.className = "tab-panel hidden admin-panel";
    panel.innerHTML =
      '<div class="adm-header">' +
        '<span class="adm-crown">👑</span>' +
        '<div>' +
          '<div class="adm-title">Founder Dashboard</div>' +
          '<div class="adm-subtitle">God Mode</div>' +
        '</div>' +
      '</div>' +
      '<div class="adm-divider"></div>' +
      '<div class="adm-metrics">' + userCards + '</div>' +
      '<div class="adm-section-title">📅 Сегодня</div>' +
      '<div class="adm-metrics">' + todayCards + '</div>' +
      '<div class="adm-section-title">🎤 Voice-to-Action</div>' +
      '<div class="adm-metrics">' + vaCards + '</div>' +
      '<div class="adm-section-title adm-ref-toggle" id="adm-growth-toggle" style="cursor:pointer">' +
        '📈 Growth Funnel <span class="adm-lazy-hint">(нажми для загрузки)</span>' +
      '</div>' +
      '<div id="adm-growth-stats"></div>' +
      '<div class="adm-section-title adm-ref-toggle" id="adm-ref-toggle" style="cursor:pointer">' +
        '🔗 Рефералы <span class="adm-lazy-hint">(нажми для загрузки)</span>' +
      '</div>' +
      '<div id="adm-ref-stats"></div>' +
      '<div class="adm-section-title adm-ref-toggle" id="adm-bc-toggle" style="cursor:pointer">' +
        '📣 Рассылки <span class="adm-lazy-hint">(нажми для загрузки)</span>' +
      '</div>' +
      '<div id="adm-bc-stats"></div>' +
      '<div class="adm-section-title adm-ref-toggle" id="adm-users-toggle" style="cursor:pointer">' +
        '👥 Пользователи <span class="adm-lazy-hint">(нажми для загрузки)</span>' +
      '</div>' +
      '<div id="adm-users-container"></div>' +
      '<div class="adm-section-title adm-ref-toggle" id="adm-log-toggle" style="cursor:pointer">' +
        '📋 Журнал действий <span class="adm-lazy-hint">(нажми для загрузки)</span>' +
      '</div>' +
      '<div id="adm-log-stats"></div>' +
      '<button class="adm-broadcast-btn" id="adm-btn-broadcast">' +
        '<span class="adm-btn-icon">📣</span>' +
        '<span>Рассылка (Broadcast)</span>' +
      '</button>' +
      '<div class="adm-footer">👁 Только ты видишь этот таб</div>';

    $("tabs-container").appendChild(panel);

    let _growthStatsLoaded = false;
    panel.querySelector("#adm-growth-toggle").addEventListener("click", async () => {
      if (_growthStatsLoaded) return;
      _growthStatsLoaded = true;
      const container = panel.querySelector("#adm-growth-stats");
      container.innerHTML = '<div style="opacity:0.5;padding:8px 0">Загрузка...</div>';
      try {
        const gs = await apiFetch("/api/admin/growth-stats");
        container.innerHTML =
          '<div class="adm-metrics">' +
            buildCards([
              { icon: "💎", value: gs.premium_screen,     label: "Открыли Premium" },
              { icon: "💳", value: gs.premium_click,      label: "Нажали оплатить" },
              { icon: "🐾", value: gs.referral_screen,    label: "Открыли реферал" },
            ]) +
          '</div>' +
          '<div class="adm-metrics">' +
            buildCards([
              { icon: "📤", value: gs.share_click,        label: "Share нажато" },
              { icon: "📋", value: gs.copy_click,         label: "Copy нажато" },
              { icon: "🔀", value: gs.share_intent_total, label: "Share intent" },
            ]) +
          '</div>';
      } catch (_) {
        container.innerHTML = '<div style="color:var(--red,#f44);padding:8px 0">Ошибка загрузки</div>';
        _growthStatsLoaded = false;
      }
    });

    let _refStatsLoaded = false;
    panel.querySelector("#adm-ref-toggle").addEventListener("click", async () => {
      if (_refStatsLoaded) return;
      _refStatsLoaded = true;
      const container = panel.querySelector("#adm-ref-stats");
      container.innerHTML = '<div style="opacity:0.5;padding:8px 0">Загрузка...</div>';
      try {
        const rs = await apiFetch("/api/admin/referral-stats");
        const msOrder = ["milestone_3", "milestone_5", "milestone_10", "milestone_25"];
        const msLabels = { milestone_3: "🥈 3 друга", milestone_5: "🥇 5 друзей", milestone_10: "💎 10 друзей", milestone_25: "👑 25 друзей" };
        const msBreakdown = msOrder
          .map(k => msLabels[k] + ": " + (rs.milestone_breakdown[k] || 0))
          .join(" · ");
        const topList = rs.top_referrers.length
          ? rs.top_referrers.map((r, i) => (i + 1) + ". " + r.telegram_id + " → " + r.count).join("<br>")
          : "Нет данных";
        container.innerHTML =
          '<div class="adm-metrics">' +
            buildCards([
              { icon: "📨", value: rs.referrals_started,   label: "Перешли по ссылке" },
              { icon: "✅", value: rs.referrals_completed, label: "Завершили онбординг" },
              { icon: "👤", value: rs.unique_referrers,    label: "Уникальных рефереров" },
            ]) +
          '</div>' +
          '<div class="adm-ref-breakdown"><b>Milestone:</b> ' + escHtml(msBreakdown) + '</div>' +
          '<div class="adm-ref-breakdown"><b>Топ-5 рефереров:</b><br>' + topList + '</div>';
      } catch (_) {
        container.innerHTML = '<div style="color:var(--red,#f44);padding:8px 0">Ошибка загрузки</div>';
        _refStatsLoaded = false;
      }
    });

    let _bcStatsLoaded = false;
    panel.querySelector("#adm-bc-toggle").addEventListener("click", async () => {
      if (_bcStatsLoaded) return;
      _bcStatsLoaded = true;
      const container = panel.querySelector("#adm-bc-stats");
      container.innerHTML = '<div style="opacity:0.5;padding:8px 0">Загрузка...</div>';
      try {
        const cs = await apiFetch("/api/admin/broadcast-stats");
        if (!cs.campaigns || cs.campaigns.length === 0) {
          container.innerHTML = '<div style="opacity:0.5;padding:8px 0">Рассылок с кнопкой пока нет</div>';
          return;
        }
        container.innerHTML = cs.campaigns.map(c =>
          '<div class="adm-ref-breakdown">' +
            '<b>' + escHtml(c.camp_id) + '</b>' +
            (c.button_text ? ' · ' + escHtml(c.button_text) : '') +
            '<br>Отправлено: ' + c.sent +
            ' &nbsp;·&nbsp; Кликов: ' + c.clicks +
            ' &nbsp;·&nbsp; CTR: ' + c.ctr + '%' +
          '</div>'
        ).join("");
      } catch (_) {
        container.innerHTML = '<div style="color:var(--red,#f44);padding:8px 0">Ошибка загрузки</div>';
        _bcStatsLoaded = false;
      }
    });

    // ── Users section ───────────────────────────────────────────────
    let _usersLoaded = false;
    panel.querySelector("#adm-users-toggle").addEventListener("click", async () => {
      if (_usersLoaded) return;
      _usersLoaded = true;
      const container = panel.querySelector("#adm-users-container");
      container.innerHTML =
        '<div style="padding:8px 0">' +
          '<input id="adm-user-search" type="text" placeholder="ID, @username или имя…" ' +
            'style="width:100%;box-sizing:border-box;padding:8px 10px;border-radius:8px;border:1px solid rgba(255,255,255,0.2);background:rgba(255,255,255,0.08);color:inherit;font-size:14px"/>' +
        '</div>' +
        '<div id="adm-users-list" style="margin-top:4px"></div>';

      const renderUsers = (users) => {
        const list = panel.querySelector("#adm-users-list");
        if (!users.length) {
          list.innerHTML = '<div style="opacity:0.5;padding:8px 0">Пользователи не найдены</div>';
          return;
        }
        list.innerHTML = users.map(u => {
          const name = escHtml((u.first_name || "") + (u.username ? " @" + u.username : ""));
          const premBadge = u.is_premium
            ? '<span style="color:#ffd700">⭐</span>' + (u.subscription_expires_at ? " до " + escHtml(u.subscription_expires_at) : "")
            : '<span style="opacity:0.5">free</span>';
          return (
            '<div class="adm-user-row" data-id="' + u.telegram_id + '">' +
              '<div class="adm-user-info">' +
                '<div class="adm-user-name">' + name + '</div>' +
                '<div class="adm-user-meta">ID: ' + u.telegram_id + ' · ' + premBadge + ' · ' + (u.created_at || "—") + '</div>' +
              '</div>' +
              '<div class="adm-user-actions">' +
                '<button class="adm-user-btn adm-grant-btn" data-id="' + u.telegram_id + '" data-name="' + escHtml(u.first_name || String(u.telegram_id)) + '">👑</button>' +
                '<button class="adm-user-btn adm-msg-btn" data-id="' + u.telegram_id + '" data-name="' + escHtml(u.first_name || String(u.telegram_id)) + '">✉️</button>' +
              '</div>' +
            '</div>'
          );
        }).join("");

        list.querySelectorAll(".adm-grant-btn").forEach(btn => {
          btn.addEventListener("click", async () => {
            const tid = parseInt(btn.dataset.id);
            const uname = btn.dataset.name;
            const days = prompt(`Grant Premium\n${uname} (${tid})\n\nКоличество дней:`);
            if (!days || !days.trim() || isNaN(parseInt(days))) return;
            try {
              const resp = await fetch("/api/admin/grant-premium", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": tg.initData || "" },
                body: JSON.stringify({ telegram_id: tid, days: parseInt(days) }),
              });
              const data = await resp.json();
              if (resp.ok) {
                tg.showAlert(`✅ Premium выдан ${data.name} до ${data.expires_at}`);
                _logLoaded = false;
              } else {
                tg.showAlert(`❌ ${data.error || resp.status}`);
              }
            } catch (_) { tg.showAlert("❌ Сетевая ошибка"); }
          });
        });

        list.querySelectorAll(".adm-msg-btn").forEach(btn => {
          btn.addEventListener("click", async () => {
            const tid = parseInt(btn.dataset.id);
            const uname = btn.dataset.name;
            const text = prompt(`Сообщение → ${uname} (${tid}):`);
            if (!text || !text.trim()) return;
            try {
              const resp = await fetch("/api/admin/send-message", {
                method: "POST",
                headers: { "Content-Type": "application/json", "X-Telegram-Init-Data": tg.initData || "" },
                body: JSON.stringify({ telegram_id: tid, text: text.trim() }),
              });
              const data = await resp.json();
              if (resp.ok) tg.showAlert(`✅ Сообщение отправлено ${uname}`);
              else tg.showAlert(`❌ ${data.error || resp.status}`);
            } catch (_) { tg.showAlert("❌ Сетевая ошибка"); }
          });
        });
      };

      const loadUsers = async (q) => {
        const list = panel.querySelector("#adm-users-list");
        list.innerHTML = '<div style="opacity:0.5;padding:8px 0">Загрузка...</div>';
        try {
          const url = q ? `/api/admin/users?q=${encodeURIComponent(q)}` : "/api/admin/users";
          const data = await apiFetch(url);
          renderUsers(data.users || []);
        } catch (_) {
          list.innerHTML = '<div style="color:var(--red,#f44);padding:8px 0">Ошибка загрузки</div>';
        }
      };

      await loadUsers("");

      let _searchTimer = null;
      panel.querySelector("#adm-user-search").addEventListener("input", (e) => {
        clearTimeout(_searchTimer);
        _searchTimer = setTimeout(() => loadUsers(e.target.value.trim()), 400);
      });
    });

    // ── Admin action log ─────────────────────────────────────────────
    let _logLoaded = false;
    panel.querySelector("#adm-log-toggle").addEventListener("click", async () => {
      if (_logLoaded) return;
      _logLoaded = true;
      const container = panel.querySelector("#adm-log-stats");
      container.innerHTML = '<div style="opacity:0.5;padding:8px 0">Загрузка...</div>';
      try {
        const data = await apiFetch("/api/admin/actions");
        const actions = data.actions || [];
        if (!actions.length) {
          container.innerHTML = '<div style="opacity:0.5;padding:8px 0">Действий пока нет</div>';
          return;
        }
        const actionEmoji = { grant_premium: "👑", grant_premium_webapp: "👑", revoke_premium: "🚫", ai_reset: "🔄", send_msg: "✉️", broadcast: "📣" };
        container.innerHTML = actions.map(a =>
          '<div class="adm-log-row">' +
            '<span class="adm-log-ts">' + escHtml(a.ts || "") + '</span> ' +
            (actionEmoji[a.action] || "·") + ' ' +
            '<b>' + escHtml(a.action || "") + '</b>' +
            (a.target ? ' → <code>' + escHtml(a.target) + '</code>' : "") +
            (a.detail ? ' <span style="opacity:0.6">(' + escHtml(a.detail) + ')</span>' : "") +
          '</div>'
        ).join("");
      } catch (_) {
        container.innerHTML = '<div style="color:var(--red,#f44);padding:8px 0">Ошибка загрузки</div>';
        _logLoaded = false;
      }
    });

    // ── Broadcast ────────────────────────────────────────────────────
    panel.querySelector("#adm-btn-broadcast").addEventListener("click", async () => {
      try { tg.HapticFeedback.impactOccurred("medium"); } catch (_) {}

      const text = prompt("Текст рассылки (поддерживается HTML):");
      if (!text || !text.trim()) return;

      const targetChoice = prompt("Аудитория:\n1 — Все (default)\n2 — Только Premium\n3 — Только Free");
      if (targetChoice === null) return;
      const targetMap = { "2": "premium", "3": "free" };
      const target = targetMap[targetChoice?.trim()] || "all";
      const targetLabel = { all: "всем", premium: "Premium", free: "Free" }[target];

      const buttonText = prompt("Текст кнопки (пусто — без кнопки):");
      if (buttonText === null) return;

      let buttonUrl = "";
      if (buttonText.trim()) {
        buttonUrl = prompt("URL кнопки:");
        if (buttonUrl === null) return;
        if (!buttonUrl.trim()) {
          tg.showAlert("❌ URL кнопки не может быть пустым");
          return;
        }
      }

      if (!confirm(`Отправить рассылку: ${targetLabel}?`)) return;

      const body = { text: text.trim(), target };
      if (buttonText.trim() && buttonUrl.trim()) {
        body.button_text = buttonText.trim();
        body.button_url  = buttonUrl.trim();
      }

      try {
        const resp = await fetch("/api/broadcast", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-Telegram-Init-Data": tg.initData || "",
          },
          body: JSON.stringify(body),
        });
        const data = await resp.json();
        if (resp.ok) {
          tg.showAlert(`✅ Рассылка (${targetLabel}) запущена для ${data.queued} пользователей`);
          _bcStatsLoaded = false;
          _logLoaded = false;
          panel.querySelector("#adm-bc-stats").innerHTML = "";
        } else {
          tg.showAlert(`❌ Ошибка: ${data.error || resp.status}`);
        }
      } catch (_e) {
        tg.showAlert("❌ Сетевая ошибка");
      }
    });
  }

  // ── Coach / Консультации tab ────────────────────────────────────────
  let _coachLoaded = false;

  async function fetchAndRenderCoach() {
    if (_coachLoaded) return;

    const list    = $("coach-threads-list");
    const empty   = $("coach-empty");
    const loading = $("coach-loading");

    list.innerHTML = "";
    hide("coach-empty");
    show("coach-loading");

    let threads;
    try {
      threads = await apiFetch("/api/coach/threads?status=all");
    } catch (_) {
      hide("coach-loading");
      list.innerHTML =
        '<div style="text-align:center;padding:40px 0;color:var(--text-sub);font-size:.85rem">' +
        _ui("coach_load_error") +
        "</div>";
      return;
    }

    _coachLoaded = true;
    hide("coach-loading");
    renderCoachThreads(threads);
  }

  function renderCoachThreads(threads) {
    const list  = $("coach-threads-list");
    const empty = $("coach-empty");
    list.innerHTML = "";

    if (!threads || threads.length === 0) {
      show("coach-empty");
      return;
    }
    hide("coach-empty");

    // Active first (by updated_at desc), then archived
    const sorted = [...threads].sort((a, b) => {
      if (a.status !== b.status) return a.status === "active" ? -1 : 1;
      return new Date(b.updated_at || 0) - new Date(a.updated_at || 0);
    });

    sorted.forEach(thread => list.appendChild(buildThreadCard(thread)));
  }

  function buildThreadCard(thread) {
    const isActive  = thread.status === "active";
    const title     = thread.title || _ui("thread_default_title");
    const dateStr   = formatRelativeDate(thread.updated_at);
    const msgCount  = thread.message_count || 0;
    const msgLabel  = msgCount + " " + pluralMsg(msgCount);

    const card = document.createElement("div");
    card.className = "thread-card" + (isActive ? "" : " thread-card--archived");
    card.dataset.threadId = thread.id;

    card.innerHTML =
      '<div class="thread-card-top">' +
        '<div class="thread-title">' + escHtml(title) + "</div>" +
        '<span class="thread-badge thread-badge--' + thread.status + '">' +
          (isActive ? _ui("thread_active") : _ui("thread_archived")) +
        "</span>" +
      "</div>" +
      '<div class="thread-meta">' +
        '<span>' + escHtml(dateStr) + "</span>" +
        '<span class="thread-meta-dot"></span>' +
        '<span>' + escHtml(msgLabel) + "</span>" +
      "</div>" +
      (thread.summary
        ? '<div class="thread-summary">' + escHtml(thread.summary) + "</div>"
        : "") +
      (isActive
        ? '<div class="thread-card-footer">' +
            '<button class="btn-archive" data-thread-id="' + thread.id + '">' + escHtml(_ui("thread_archive_btn")) + '</button>' +
          "</div>"
        : "");

    // Card click → prompt to go to bot
    card.addEventListener("click", (e) => {
      if (e.target.closest(".btn-archive")) return;
      const msg = isActive
        ? _ui("thread_click_active", {title: title})
        : _ui("thread_click_archived", {title: title});
      try { tg.showAlert(msg); } catch (_) {}
    });

    // Archive button
    if (isActive) {
      card.querySelector(".btn-archive").addEventListener("click", async (e) => {
        e.stopPropagation();
        await archiveThread(thread, card);
      });
    }

    return card;
  }

  async function archiveThread(thread, cardEl) {
    const btn = cardEl.querySelector(".btn-archive");
    if (!btn) return;
    btn.classList.add("btn-archive--loading");
    btn.textContent = "...";

    try {
      await apiFetch("/api/coach/threads/" + thread.id + "/archive", { method: "PATCH" });
    } catch (_) {
      btn.classList.remove("btn-archive--loading");
      btn.textContent = _ui("thread_archive_btn");
      try { tg.showAlert(_ui("thread_archive_error")); } catch (_) {}
      return;
    }

    // Update card to archived state in-place
    thread.status = "archived";
    cardEl.classList.add("thread-card--archived");
    cardEl.style.transition = "opacity 300ms ease, transform 300ms ease";
    cardEl.style.opacity = "0";
    cardEl.style.transform = "scale(0.97)";

    setTimeout(() => {
      // Remove from top (active), re-insert at bottom of list
      const list = $("coach-threads-list");
      cardEl.style.opacity = "";
      cardEl.style.transform = "";
      cardEl.querySelector(".thread-badge").className = "thread-badge thread-badge--archived";
      cardEl.querySelector(".thread-badge").textContent = _ui("thread_archived");
      const footer = cardEl.querySelector(".thread-card-footer");
      if (footer) footer.remove();
      list.appendChild(cardEl);
      requestAnimationFrame(() => { cardEl.style.opacity = "1"; });
      try { tg.HapticFeedback.impactOccurred("light"); } catch (_) {}
    }, 250);
  }

  function formatRelativeDate(isoStr) {
    if (!isoStr) return "";
    const d       = new Date(isoStr);
    const now     = new Date();
    const diffMs  = now - d;
    const diffDay = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    if (diffDay === 0) return _ui("date_today");
    if (diffDay === 1) return _ui("date_yesterday");
    if (diffDay < 7)  return _ui("date_days_ago", {n: diffDay});
    return d.toLocaleDateString(_ui("date_locale"), { day: "numeric", month: "short" });
  }

  function pluralMsg(n) {
    const mod10 = n % 10, mod100 = n % 100;
    if (mod10 === 1 && mod100 !== 11) return _ui("msg_1");
    if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return _ui("msg_2");
    return _ui("msg_many");
  }

  // ── Boot ───────────────────────────────────────────────────────────
  load();
})();
