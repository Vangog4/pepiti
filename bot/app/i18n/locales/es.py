"""Español/Mexicano (es) — Spanish (Latin America) translation."""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Pepito — Entrenador IA para perros</b>",
    "menu.main.choose": "Elige una sección:",
    "menu.btn.training": "🏋️ Entreno",
    "menu.btn.week_plan": "📅 Semana",
    "menu.btn.stats": "📊 Estadística",
    "menu.btn.coach": "💬 Entrenador",
    "menu.btn.profile": "🐶 Pasaporte",
    "menu.btn.premium": "⭐ Premium",
    "menu.btn.premium.active": "⭐ Premium ✓",
    "menu.btn.shop": "🛒 Tienda",
    "menu.btn.invite": "🎁 Amigos",
    "menu.btn.webapp": "📱 App",
    "menu.main.streak": "{emoji} Entrenamientos completados: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "día",
    "menu.main.streak.days.few": "días",
    "menu.main.streak.days.many": "días",
    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 Menú",
    "common.back.btn": "🔙 Atrás",
    "common.menu.btn": "🔙 Menú",
    # ── Errors / Guards ────────────────────────────────────────────────────────
    "error.no_pet": "Por favor, completa primero el registro: /start",
    # ── Settings ───────────────────────────────────────────────────────────────
    "settings.main.title": "⚙️ <b>Configuración</b>",
    "settings.main.reminder_on": "⏰ Recordatorios: <b>{time} ({tz})</b>",
    "settings.main.reminder_default": "⏰ Recordatorios: <b>10:00 ({tz})</b> (predeterminado)",
    "settings.main.reminder_off": "⏰ Recordatorios: <b>desactivados</b>",
    "settings.language.title": "🌐 <b>Idioma</b>",
    "settings.language.choose": "Elige el idioma de la interfaz:",
    "settings.language.saved": "✅ Idioma cambiado a <b>{name}</b>.",
    "settings.language.btn": "🌐 Idioma",
    "settings.btn": "⚙️ Ajustes",
    "settings.reminder.btn": "⏰ Recordatorios",
    # ── Onboarding (Stage 9: conversational AI) ────────────────────────────────
    "onboarding.start.returning": "¡Bienvenido/a de vuelta, {name}! 🐾\n¿Qué hacemos hoy?",
    "onboarding.ai.welcome": (
        "¡Hola, <b>{name}</b>! Soy Pepito — tu entrenador IA para perros. 🐶\n\n"
        "Cuéntame sobre tu perro: nombre, raza, edad y qué desafíos tienen juntos.\n\n"
        "<i>Puedes escribir o enviar un mensaje de voz.</i>\n\n"
        "<b>Ejemplo:</b> «Beagle Charlie, 2 años, jala la correa y ladra a otros perros»"
    ),
    "onboarding.ai.thinking": "⏳ <i>Analizando...</i>",
    "onboarding.ai.photo_prompt": (
        "📷 ¡Qué mascota tan linda! Cuéntame más por texto o voz:\n"
        "nombre, raza, edad y en qué necesitas ayuda?"
    ),
    "onboarding.ai.clarify": "¡Anotado — <b>{summary}</b>!\n\n{question}",
    "onboarding.ai.clarify.name": "¿Cómo se llama tu mascota?",
    "onboarding.ai.clarify.breed": "¿De qué raza es?",
    "onboarding.ai.clarify.age_category": "¿Cuántos años tiene? (cachorro, joven o adulto?)",
    "onboarding.done.welcome": (
        "🎉 <b>¡Perfil creado!</b>\n\n"
        "¡Bienvenido/a, {name}!\n"
        "Estoy listo para ayudarte a entrenar a <b>{pet}</b>."
    ),
    "onboarding.done.referral_bonus": "\n\n🎁 <b>Bono de referido:</b> ¡+{days} días Premium activados!",
    "onboarding.done.milestone": "\n🏆 <b>Hito de referido:</b> {label} — ¡{reward}!",
    "onboarding.done.plan_loading": "🐾 <i>Creando el primer plan de entrenamiento para {pet}...</i>",
    "onboarding.done.first_plan": "🏋️ <b>¡Aquí está tu primer plan!</b>\n\n{plan}",
    "onboarding.done.fallback": "Elige por dónde empezar 👇",
    # ── Training ───────────────────────────────────────────────────────────────
    "training.loading": "🐾 <i>Creando un plan para {name}...</i>",
    "training.refresh.confirm": "🔄 <b>¿Generar un nuevo plan?</b>\n\nTu progreso actual se reiniciará.",
    "training.refresh.confirm.yes": "✅ Sí, nuevo plan",
    "training.refresh.confirm.no": "❌ No",
    "training.refresh.loading": "🔄 <i>Generando nuevo plan para {name}...</i>",
    "training.refresh.toast": "Generando nuevo plan…",
    "training.week.loading": "📅 <i>Creando plan semanal para {name}...</i>",
    "training.week.refresh.confirm": (
        "🔄 <b>¿Generar un nuevo plan semanal?</b>\n\nTu progreso semanal actual será reiniciado."
    ),
    "training.week.refresh.loading": "🔄 <i>Generando nuevo plan semanal para {name}...</i>",
    "training.week.empty": (
        "📅 <b>Plan semanal</b>\n\n"
        "🌱 <b>Aún no hay tareas</b>\n\n"
        "Empieza con el plan diario — Pepito creará el plan semanal "
        "¡una vez que tengas algo de progreso!"
    ),
    "training.week.empty.cta.btn": "🏋️ Entrenamiento de hoy",
    "training.explain.btn": "📖 Explicar",
    "training.refresh.btn": "🔄 Nuevo plan",
    "training.explain.loading": "🔍 <i>Explicando el ejercicio «{title}»...</i>",
    "training.explain.back_daily.btn": "🔙 Volver al entrenamiento",
    "training.explain.back_weekly.btn": "🔙 Volver al plan",
    "training.task.not_found": "Tarea no encontrada.",
    "training.plan.not_found": "Plan no encontrado.",
    "training.task.toggle.done": "✅ ¡Hecho!",
    "training.task.toggle.undone": "↩️ Deshecho",
    "training.share.text": "¡{name} y yo hemos entrenado {n} {days} seguidos con Pepito! 🐾",
    "training.share.btn": "📤 Compartir",
    "training.done": (
        "\n\n🎉 <b>¡Entrenamiento completado! ¡Excelente trabajo!</b>\n"
        "{emoji} Entrenamientos en total: {n}"
    ),
    "training.week_done": (
        "\n\n🎉 <b>¡{day} completado! ¡Excelente trabajo!</b>\n{emoji} Entrenamientos en total: {n}"
    ),
    "training.stats.empty": (
        "🌱 <b>¡Apenas estás comenzando!</b>\n\n"
        "Tu primera sesión es la más importante.\n"
        "Abre el plan de hoy y marca el primer ejercicio como hecho — "
        "¡tu contador de entrenamientos comenzará a crecer!"
    ),
    "training.stats.empty.cta": "🏋️ Comenzar entrenamiento",
    "training.minutes.abbr": "min",
    "training.goal.label": "Objetivo",
    "training.day.1": "Lunes",
    "training.day.2": "Martes",
    "training.day.3": "Miércoles",
    "training.day.4": "Jueves",
    "training.day.5": "Viernes",
    "training.day.6": "Sábado",
    "training.day.7": "Domingo",
    "training.day.short.1": "Lu",
    "training.day.short.2": "Ma",
    "training.day.short.3": "Mi",
    "training.day.short.4": "Ju",
    "training.day.short.5": "Vi",
    "training.day.short.6": "Sá",
    "training.day.short.7": "Do",
    "coach.display.photo": "[📷 Foto]",
    "coach.display.voice": "[🎤 Voz]",
    "coach.display.video": "[🎥 Video]",
    "defaults.pet_name": "Mascota",
    # ── AI / Coach ─────────────────────────────────────────────────────────────
    "ai.fallback": (
        "🧠 <b>El entrenador está gestionando demasiadas solicitudes ahora mismo</b>\n\n"
        "Inténtalo de nuevo en un momento — esto suele resolverse rápido.\n"
        "<i>Si el problema persiste, escribe /menu e inténtalo de nuevo.</i>"
    ),
    "ai.rate_limit": (
        "💬 <b>Límite diario alcanzado</b>\n\n"
        "Gratis: <b>{limit} solicitudes IA por día</b>\n"
        "El límite se reinicia a la tu medianoche local.\n\n"
        "⭐ <b>Premium — ilimitado:</b>\n"
        "💬 Preguntas ilimitadas al entrenador\n"
        "🧠 Análisis detallado del progreso\n"
        "🎁 Recomendaciones personalizadas"
    ),
    "ai.rate_limit.btn": "⭐ Premium",
    "ai.analyzing.premium": "🧠 <i>Realizando análisis detallado...</i>",
    "ai.analyzing.free": "🧠 <i>Analizando progreso...</i>",
    "ai.progress.premium.header": "⭐ <b>Análisis detallado para {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Análisis de progreso para {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 Volver a estadísticas",
    "ai.retry.btn": "🔄 Reintentar",
    "ai.back_menu.btn": "🔙 Menú",
    "coach.entry": (
        "💬 <b>Pregunta al entrenador</b>\n\n"
        "Haz cualquier pregunta sobre adiestramiento o comportamiento — o envía una <b>📷 foto</b>.\n"
        "<i>Ej.: «¿Cómo evito que jale la correa?» o «¿Por qué ignora la orden “Quieto”?»</i>\n\n"
        "Gratis: texto + foto\n"
        "⭐ Premium: + 🎤 mensajes de voz y 🎥 videos"
    ),
    "coach.thinking": "🧠 <i>Analizando tu pregunta...</i>",
    "coach.media.thinking": "🔍 <i>Analizando medios...</i>",
    "coach.media.voice.premium": (
        "🎤 <b>Análisis de voz — solo Premium</b>\n\n"
        "Envía una <b>📷 foto</b> de tu perro — es gratis.\n\n"
        "⭐ Premium desbloquea análisis de voz y video sin límites."
    ),
    "coach.media.video.premium": (
        "🎥 <b>Análisis de video — solo Premium</b>\n\n"
        "Envía una <b>📷 foto</b> de tu perro — es gratis.\n\n"
        "⭐ Premium desbloquea análisis de video y voz sin límites."
    ),
    "coach.media.too_large": "⚠️ Archivo demasiado grande (máx 20 MB). Intenta enviar un clip más corto.",
    "coach.hub.active_thread": (
        "💬 <b>Entrenador</b> · <i>{title}</i>\n\n"
        "{count} mens. · en curso\n\n"
        "Escribe una pregunta o envía una foto."
    ),
    "coach.hub.archive_btn": "📁 Finalizar consulta",
    "coach.new_thread.btn": "🆕 Nuevo tema",
    "coach.thread.archived": "✔ Consulta finalizada.",
    "coach.thread.title_default": "Consulta",
    "coach.role.owner": "Dueño",
    "coach.role.trainer": "Entrenador",
    "coach.summary.header": "Breve resumen de la conversación anterior:",
    # ── Voice-action (hands-free task reporting) ───────────────────────────────
    "voice_action.thinking": "🐾 <i>Analizando...</i>",
    "voice_action.marked": "✅ ¡Marqué la tarea <b>{task}</b> como completada!\n\n",
    "voice_action.all_done": "🎉 ¡Todas las tareas del día completadas! ¡Gran entrenamiento!",
    # ── Stats ──────────────────────────────────────────────────────────────────
    "stats.header": "📊 <b>Estadísticas de {name}</b>\n\n",
    "stats.days_with_us": "🗓 Días con Pepito: <b>{n}</b>\n",
    "stats.completed": "{emoji} Sesiones completadas: <b>{n}</b>\n\n",
    "stats.level": "🏆 Nivel de obediencia: <b>{level}</b>\n\n",
    "stats.motivate": "<i>¡Cada sesión hace a {name} mejor!</i> 🚀",
    "stats.analysis.premium.btn": "🧠 Análisis IA detallado ⭐",
    "stats.analysis.free.btn": "🧠 Análisis IA de progreso",
    # ── Profile ────────────────────────────────────────────────────────────────
    "profile.header": "🐾 <b>{name}</b>\n\n",
    "profile.breed": "🐕 Raza: {val}\n",
    "profile.sex": "⚥ Sexo: {val}\n",
    "profile.age": "🎂 Edad: {val}\n",
    "profile.size": "📏 Tamaño: {val}\n",
    "profile.weight": "⚖️ Peso: {val}\n\n",
    "profile.level": "🎓 Nivel: {val}/5\n",
    "profile.goal": "🎯 Objetivo: {val}\n",
    "profile.issues": "📋 Problemas: {val}\n",
    "profile.schedule": "🗓 Horario: {val}\n\n",
    "profile.training_count": "🔥 Sesiones completadas: <b>{n}</b>",
    "profile.weight.unit": "kg",
    "profile.weight.unknown": "no especificado",
    "profile.issues.none": "ninguno",
    "profile.schedule.unknown": "no especificado",
    "profile.edit.btn": "✏️ Editar perfil",
    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>Tienda PepitoPet</b>",
    "shop.body": (
        "Premios naturales artesanales — "
        "sin aditivos ni conservadores, solo carne real.\n\n"
        "Elige una categoría:"
    ),
    "shop.cat.training.btn": "🎯 Premios de entrenamiento",
    "shop.cat.longplay.btn": "🦴 Masticables de larga duración",
    "shop.cat.by_size.btn": "🐶 Cachorros & por tamaño",
    "shop.cat.all.btn": "🛒 Tienda completa",
    "shop.rec.puppy_named": "🐶 Premios para cachorros — para {name}",
    "shop.rec.small_named": "🐶 Premios para razas pequeñas — para {name}",
    "shop.rec.puppy_small_free": "🐶 Premios para cachorros y perros pequeños",
    "shop.rec.longplay_named": "🎁 Premios de larga duración — premio para {name}",
    "shop.rec.longplay_free": "🦴 Premios de larga duración",
    "shop.rec.exercise_named": "🦴 Premios de ejercicio para {name}",
    "shop.rec.training_named": "🦴 Premios de entrenamiento para {name}",
    "shop.rec.training_free": "🦴 Premios de entrenamiento",
    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>¡Invita a un amigo — bono para ambos!</b>",
    "invite.link_label": "🔗 Tu enlace:",
    "invite.bonus": "🎁 Cada amigo da <b>+{days} días Premium</b> — a ti <i>y</i> a él/ella.",
    "invite.ladder.title": "🏆 <b>Camino de recompensas:</b>",
    "invite.count": "👥 Invitados: <b>{n}</b>",
    "invite.next": "🎯 Hasta la siguiente recompensa: <b>{n}</b> más",
    "invite.all_done": "👑 <b>¡Todas las recompensas obtenidas! ¡Eres una leyenda!</b>",
    "invite.share.btn": "📤 Compartir enlace",
    "invite.share.text": "Entreno a mi mascota con Pepito entrenador IA 🐾",
    "invite.base_tier": "1 amigo    — +{days} días Premium (para ambos)",
    "invite.goal": "🎯 {needed} más para {next_label} ({reward})",
    "invite.current_goal": "← siguiente meta",
    "invite.how.title": "❓ <b>Cómo funciona:</b>",
    "invite.how.1": "1. Comparte tu enlace",
    "invite.how.2": "2. El amigo inicia el bot y completa su perfil",
    "invite.how.3": "3. Ambos reciben +{days} días Premium",
    # ── Referral push-notifications ────────────────────────────────────────────
    "referral.notify.base": (
        "🎉 ¡Un nuevo amigo se unió a través de tu enlace!\n"
        "+{days} días Premium añadidos. Invitados: <b>{count}</b>\n{ladder_hint}"
    ),
    "referral.notify.milestone": (
        "🏆 <b>¡{label}!</b>\n\n"
        "¡Has invitado a {count} amigos y ganas <b>{reward}</b>!\n{next_hint}"
    ),
    "referral.notify.next_hint": "🎯 Próximo objetivo: {next_label} → {next_reward}",
    "referral.notify.all_done": "👑 ¡Todas las recompensas desbloqueadas!",
    "referral.milestone.label.3": "3 amigos",
    "referral.milestone.label.5": "5 amigos",
    "referral.milestone.label.10": "10 amigos",
    "referral.milestone.label.25": "25 amigos",
    "referral.reward.days": "+{days} días",
    # ── Premium / Subscription ─────────────────────────────────────────────────
    "premium.active.title": "⭐ <b>Premium activo</b>",
    "premium.active.expires": "Válido hasta: <b>{date}</b>",
    "premium.active.features": (
        "\n\nIncluido:\n"
        "💬 Preguntas ilimitadas al entrenador\n"
        "🧠 Análisis IA detallado del progreso\n"
        "🎁 Recomendaciones de premios personalizadas"
    ),
    "premium.upsell.body": (
        "⭐ <b>Pepito Premium</b>\n\n"
        "💬 Preguntas al entrenador — sin límites\n"
        "🧠 Análisis IA detallado del progreso\n"
        "🎁 Recomendaciones personalizadas de premios\n\n"
        "<b>{price} Stars</b> / mes · o invita a 3 amigos — gratis"
    ),
    "premium.upsell.btn": "⭐ Obtener Premium por {price} Stars",
    "premium.invoice.title": "Pepito Premium — 1 mes",
    "premium.invoice.description": "Entrenador IA ilimitado, reportes detallados y análisis conductual profundo.",
    "premium.invoice.label": "Premium 1 mes",
    "premium.activated": (
        "🎉 <b>¡Premium activado!</b>\n\n"
        "Ahora disponible:\n"
        "💬 Preguntas ilimitadas al entrenador\n"
        "🧠 Análisis detallado del progreso\n"
        "🎁 Recomendaciones de premios personalizadas\n\n"
        "Usa /menu para empezar."
    ),
    "premium.paysupport": "💬 <b>Soporte de pagos</b>\n\n¿Pagaste y no tienes Premium? ¿Necesitas un reembolso? Escribe a soporte con el ID del pago de tu chat de Telegram. Respondemos en un día.",
    "premium.terms": "📄 <b>Términos</b>\n\nPremium es una suscripción digital al entrenador canino con IA Pepito, pagada con Telegram Stars. Se renueva sola y puedes cancelarla cuando quieras en los ajustes de Telegram. Reembolsos: /paysupport. El bot no sustituye al veterinario.",
    "premium.plan.premium_1m.btn": "1 mes · {stars}⭐",
    "premium.plan.premium_3m.btn": "3 mes · {stars}⭐",
    "premium.plan.premium_12m.btn": "12 mes · {stars}⭐",
    "premium.plans.btn": "Planes",
    "ai.remaining": "Hoy quedan {n} de {limit}",
    "onboarding.q.name": "🐶 ¡Hola! Soy Pepito, tu entrenador canino. ¿Cómo se llama tu perro?",
    "onboarding.q.age": "¿Cuántos años tiene <b>{name}</b>?",
    "onboarding.q.breed": "¿Qué raza? Elige o envía una foto.",
    "onboarding.q.breed_text": "Escribe la raza o envía una foto 📷",
    "onboarding.q.goal": "¿Qué quieres trabajar?",
    "onboarding.photo.fail": "No pude ver la raza 🤔 Escríbela, por favor.",
    "onboarding.photo.guess": "Parece: <b>{breed}</b>. ¿Correcto?",
    "onboarding.btn.other": "Otra",
    "onboarding.btn.photo": "📷 Foto",
    "onboarding.age.1": "Menos de 4 m",
    "onboarding.age.2": "4–12 meses",
    "onboarding.age.3": "1–3 años",
    "onboarding.age.4": "3–7 años",
    "onboarding.age.5": "7+ años",
    "onboarding.goal.1": "Obediencia",
    "onboarding.goal.2": "Conducta",
    "onboarding.goal.3": "Cachorro",
    "onboarding.goal.4": "Actividad",
    "onboarding.name.need_text": "Escribe el nombre 🙂",
    "memory.btn": "🧠 Memoria",
    "memory.title": "🧠 <b>Lo que recuerdo de {name}</b>\n──────────",
    "memory.empty": "🧠 Aún no recuerdo nada de <b>{name}</b>. Cuéntame en el chat o añade un dato tú mismo.",
    "memory.add.btn": "➕ Añadir",
    "memory.add.prompt": "Escribe un dato de tu perro en una frase, p. ej. «le asustan los truenos».",
    "memory.add.invalid": "Envía entre 3 y 160 caracteres 🙂",
    "memory.deleted": "Eliminado",
    "edit_profile.btn.weight": "⚖️ Peso",
    "edit_profile.btn.birth": "🎂 Nacimiento",
    "edit_profile.btn.allergies": "🚫 Alergias",
    "edit_profile.btn.chronic": "🩺 Crónicas",
    "edit_profile.field.weight.prompt": "Envía el peso en kg, p. ej. 12,5",
    "edit_profile.field.birth.prompt": "Envía la fecha de nacimiento: 31.12.2023",
    "edit_profile.field.allergies.prompt": "Lista las alergias separadas por comas o envía «ninguna»",
    "edit_profile.field.chronic.prompt": "Lista las condiciones crónicas separadas por comas o envía «ninguna»",
    "edit_profile.error.invalid": "No pude entenderlo. Revisa el formato e inténtalo de nuevo.",
    "profile.allergies": "🚫 Alergias: {val}\n",
    "profile.chronic": "🩺 Crónicas: {val}\n",
    "menu.btn.health": "🩺 Salud",
    "health.title": "🩺 <b>Salud de {name}</b>\n──────────",
    "health.kind.vaccine": "Vacuna",
    "health.kind.ticks": "Garrapatas",
    "health.kind.worms": "Gusanos",
    "health.row.none": "{kind}: sin registrar",
    "health.row.overdue": "{kind}: ⚠️ atrasado {n} d",
    "health.row.today": "{kind}: ❗ hoy",
    "health.row.soon": "{kind}: ⏳ en {n} d ({date})",
    "health.row.later": "{kind}: ✅ hasta {date}",
    "health.add.prompt": "¿Cuándo se hizo: {kind}?",
    "health.btn.today": "Hoy",
    "health.btn.date": "Fecha",
    "health.btn.back": "🔙 Atrás",
    "health.date.prompt": "Envía la fecha como 31.10.2026",
    "health.date.invalid": "No pude leer la fecha. Envía una fecha pasada como 31.10.2026.",
    "health.saved": "✅ Registrado: {kind}. Próxima vez — {date}.",
    "health.push.soon": "🔔 {name}: {kind} en {n} d ({date})",
    "health.push.today": "🔔 {name}: toca hoy — {kind}",
    "health.btn.done": "✅ Hecho",
    "health.btn.snooze": "⏰ +3 días",
    "health.snoozed": "Vale, te lo recuerdo el {date}.",
    "menu.btn.tracker": "🔥 Racha",
    "tracker.title": "🔥 <b>Seguimiento de {name}</b>\n──────────",
    "tracker.streak": "Racha: <b>{n}</b> días seguidos",
    "tracker.streak.zero": "Racha: 0 por ahora. ¡Entrena hoy y empieza!",
    "tracker.today.done": "Hoy: ✅ hecho",
    "tracker.today.todo": "Hoy: aún no",
    "tracker.freezes": "🧊 Congelaciones esta semana: {n}",
    "tracker.week": "Esta semana: {days} entrenos, {walks} paseos ({minutes} min)",
    "tracker.badges": "Logros: {list}",
    "tracker.walk.btn": "🚶 {m} min",
    "tracker.walk.saved": "Paseo guardado: {m} min",
    "tracker.badge.new": "🎉 Nuevo logro: {badge}",
    "tracker.badge.streak_7": "🔥7 días",
    "tracker.badge.streak_30": "⚡30 días",
    "tracker.badge.streak_100": "🏆100 días",
    "tracker.badge.walks_10": "🚶10 paseos",
    "report.weekly.stats": "📊 <b>Tu semana, {name}</b>\n\n🐶 {pet}\n🏋️ Entrenos: {days}\n🚶 Paseos: {walks} ({minutes} min)\n🔥 Racha: {streak} días\n\n¡Buen trabajo! El lunes llega un plan nuevo.",
    "menu.btn.more": "⚙️ Más",
    "menu.more.title": "Elige una sección 👇",
    "media.verdict.vet_now": "🚨 <b>Ve al veterinario hoy</b>",
    "media.verdict.vet_soon": "⚠️ <b>Muéstraselo al veterinario en unos días</b>",
    "media.verdict.see": "🎯 <b>Lo que veo:</b>",
    "media.verdict.steps": "🛠 <b>Qué hacer:</b>",
    "media.verdict.disclaimer": "<i>No es un diagnóstico ni sustituye al veterinario.</i>",
    "card.unit.streak": "días seguidos",
    "card.headline.streak": "{pet} no falta a un entreno",
    "card.badge.caption": "Nuevo logro",
    "card.week.caption": "entrenos esta semana",
    "card.row.walks": "Paseos",
    "card.row.minutes": "Minutos de paseo",
    "card.row.streak": "Racha, días",
    "card.row.age": "Edad",
    "card.row.weight": "Peso",
    "card.row.allergies": "Alergias",
    "card.unit.kg": "kg",
    "card.passport.caption": "Pasaporte canino",
    "card.nothing": "Aún no hay nada que compartir. Entrena hoy y aparecerá la tarjeta.",
    "card.drawing": "Dibujando la tarjeta…",
    "card.error": "No se pudo dibujar la tarjeta. Inténtalo más tarde.",
    "card.caption": "¡Aquí tienes! Súbela a Stories 🐶",
    "tracker.card.streak.btn": "📤 Racha",
    "tracker.card.week.btn": "📤 Semana",
    "tracker.card.badge.btn": "📤 Logro",
    "profile.card.btn": "📤 Tarjeta",
    "nudge.renew.soon": "⏳ Premium termina en {n} días ({date}). ¿Renovar para que {pet} no pierda las respuestas ilimitadas ni la memoria?",
    "nudge.renew.last": "⏳ Premium termina mañana ({date}). Renueva para conservar las respuestas ilimitadas y la memoria de {pet}.",
    "nudge.renew.btn": "⭐ Renovar",
    "nudge.evening": "🔥 Racha de {n} días — hoy aún no has entrenado con {pet}. ¡5 minutos la mantienen viva!",
    "nudge.season.ticks": "🕷 {pet}: empezó la temporada de garrapatas. Revísalo tras cada paseo y no olvides el tratamiento: anótalo en Salud.",
    "nudge.season.heat": "☀️ ¡Calor! Pasea a {pet} de mañana y de tarde, dale mucha agua y prueba el asfalto con la mano.",
    "nudge.season.reagents": "🧂 Invierno y sal en las calles: lava las patas de {pet} tras el paseo y usa cera protectora.",
    "nudge.winback": "👋 {pet} echa de menos los entrenos. Con Premium vuelven las preguntas ilimitadas, la memoria y las tarjetas. ¿Vuelves?",
    "nudge.winback.btn": "⭐ Volver",
    "settings.seasonal.on": "🌦 Época: sí",
    "settings.seasonal.off": "🌦 Época: no",
    "settings.seasonal.toast.on": "Consejos de temporada activados",
    "settings.seasonal.toast.off": "Consejos de temporada desactivados",
    "profile.pdf.btn": "📄 Veterinario",
    "pdf.drawing": "Preparando el PDF…",
    "pdf.caption": "Pasaporte para el veterinario. Datos aportados por el dueño.",
    "pdf.passport.title": "Pepito — pasaporte canino",
    "pdf.passport.profile": "Perfil",
    "pdf.passport.breed": "Raza",
    "pdf.passport.sex": "Sexo",
    "pdf.passport.age": "Edad",
    "pdf.passport.birth": "Fecha de nacimiento",
    "pdf.passport.weight": "Peso",
    "pdf.passport.kg": "kg",
    "pdf.passport.health": "Salud",
    "pdf.passport.allergies": "Alergias",
    "pdf.passport.chronic": "Condiciones crónicas",
    "pdf.passport.notes": "Notas",
    "pdf.passport.schedule": "Vacunas y tratamientos",
    "pdf.passport.last": "hecho",
    "pdf.passport.next": "próximo",
    "pdf.passport.history": "Historial",
    "pdf.passport.facts": "Lo que se sabe del perro",
    "pdf.passport.disclaimer": "Generado el {date} por Pepito (@pepitopetbot) con datos del dueño. No es un documento médico.",
    "premium.refunded": (
        "✔ Tu reembolso ha sido procesado. Suscripción Premium desactivada.\n"
        "Si esto es un error, por favor contacta al soporte."
    ),
    "webapp.validation.name_empty": "El nombre no puede estar vacío",
    "webapp.validation.name_long": "Nombre: máximo 30 caracteres",
    "webapp.validation.breed_long": "Raza: máximo 40 caracteres",
    "webapp.validation.goal_long": "Objetivo: máximo 150 caracteres",
    "webapp.validation.level": "Nivel de entrenamiento no válido",
    "webapp.validation.age": "Categoría de edad no válida",
    "webapp.validation.reminder": "Formato: HH:MM, ej. 09:30",
    "webapp.validation.timezone": "Zona horaria no válida",
    "webapp.validation.language": "Idioma no válido",
    # ── Reminders ─────────────────────────────────────────────────────────────
    "reminder.title": "⏰ <b>Recordatorios</b>",
    "reminder.status.off": "🔕 <b>Desactivado</b>",
    "reminder.status.off.desc": "Los recordatorios diarios no están activos.",
    "reminder.status.on": "🔔 <b>Activado</b> — {time} ({tz}) cada día",
    "reminder.status.default": "🔔 <b>Activado</b> — 10:00 ({tz}, predeterminado)",
    "reminder.status.on.desc": "Pepito te recordará entrenar a tu mascota.",
    "reminder.input.prompt": (
        "⏰ <b>Recordatorios</b>\n\n"
        "Ingresa la hora en formato <code>HH:MM</code> en tu zona horaria (<b>{tz}</b>).\n"
        "Ejemplos: <code>09:00</code>, <code>18:30</code>\n\n"
        "<i>Puedes cambiar tu zona horaria en ✏️ Editar perfil → 🌍 Zona horaria.</i>"
    ),
    "reminder.disabled": ("🔕 <b>Desactivado</b>\nYa no recibirás recordatorios diarios."),
    "reminder.saved": "✅ <b>¡Listo!</b> Recordatorio configurado para <b>{time} ({tz})</b> cada día.",
    "reminder.error.format": (
        "⚠️ Formato inválido. Ingresa la hora como <code>HH:MM</code>, ej. <code>09:30</code>."
    ),
    "reminder.enable.btn": "🔔 Activar recordatorios",
    "reminder.change.btn": "✏️ Cambiar hora",
    "reminder.disable.btn": "🔕 Desactivar",
    "reminder.back.btn": "🔙 Volver a recordatorios",
    "reminder.back_settings.btn": "🔙 Atrás",
    "reminder.settings.btn": "⏰ Configuración de recordatorios",
    "reminder.menu.btn": "🔙 Menú",
    "reminder.tz_missing": "⚠️ <b>Zona horaria no configurada</b> — se usa UTC+0. Configúrala para que los recordatorios lleguen a la hora correcta.",
    "reminder.tz_change.btn": "🌍 Configurar zona horaria",
    "reminder.push.friend": "amigo",
    "reminder.push.text": "🐾 ¡Hola, {name}!\n\nNo olvides entrenar con tu mascota hoy. Abre /menu para ver el plan.",
    "report.weekly.premium": (
        "📊 Informe semanal, {name}!\n\n"
        "Total de días de entrenamiento: <b>{days}</b>\n"
        "¡Sigue así! Abre /menu para más detalles."
    ),
    "report.weekly.free": (
        "📊 Resumen semanal, {name}!\n\n"
        "Días de entrenamiento: <b>{days}</b>\n"
        "Obtén análisis detallados con Premium — /menu."
    ),
    # ── Help / Support ─────────────────────────────────────────────────────────
    "help.guide.title": "❓ <b>Guía de Pepito</b>\n\n",
    "help.guide.plan.header": "🧠 <b>Cómo funcionan los planes de entrenamiento</b>\n",
    "help.guide.plan.text": (
        "Pepito genera un plan cada día basado en el perfil de tu mascota. "
        "Toca «🏋️ Entrenamiento de hoy» para ver tu lista de tareas.\n\n"
    ),
    "help.guide.streak.header": "✅ <b>Casillas de verificación & progreso</b>\n",
    "help.guide.streak.text": (
        "Marca ○ → ✅ cada ejercicio. Completa todas las tareas y el día cuenta — "
        "tu total de entrenamientos crece.\n\n"
    ),
    "help.guide.shop.header": "🛍️ <b>Tienda & recompensas</b>\n",
    "help.guide.shop.text": (
        "Después del entrenamiento Pepito recomienda premios naturales de PepitoPet. "
        "Invita amigos — gana bonos: +30, +60, +90 y +180 días Premium en los hitos.\n\n"
    ),
    "help.guide.premium.header": "⭐ <b>Qué te da Premium</b>\n",
    "help.guide.premium.text": (
        "💬 Preguntas ilimitadas al entrenador\n"
        "🧠 Análisis IA detallado del progreso\n"
        "🎁 Recomendaciones personalizadas con el nombre de tu mascota\n\n"
    ),
    "help.guide.commands": "<b>Comandos:</b> /menu · /start · /reset",
    "help.support.btn": "💬 Contactar soporte",
    "help.btn": "❓ Ayuda",
    "help.back_settings.btn": "🔙 Volver a configuración",
    # ── Edit Profile ───────────────────────────────────────────────────────────
    "edit_profile.title": "✏️ <b>Editar perfil</b>\n\n¿Qué deseas cambiar?",
    "edit_profile.field.name.prompt": "Escribe el nuevo nombre de tu mascota en el chat:",
    "edit_profile.field.breed.prompt": "Escribe la nueva raza en el chat:",
    "edit_profile.field.goal.prompt": "Escribe el nuevo objetivo de entrenamiento en el chat:",
    "edit_profile.field.level.prompt": "Elige el nuevo nivel de obediencia:",
    "edit_profile.field.age.prompt": "Elige la nueva categoría de edad:",
    "edit_profile.field.size.prompt": "Elige el nuevo tamaño de tu mascota:",
    "edit_profile.field.timezone.prompt": "🌍 Elige tu zona horaria:",
    "edit_profile.saved": "✅ Actualizado: <b>{value}</b>",
    "edit_profile.edit_more.btn": "✏️ Editar más",
    "edit_profile.error.empty": "⚠️ El campo no puede estar vacío. Inténtalo de nuevo.",
    "edit_profile.error.too_long": "⚠️ Valor demasiado largo — máximo 50 caracteres (el tuyo: {n}).",
    "edit_profile.btn.name": "🐾 Nombre",
    "edit_profile.btn.breed": "🐕 Raza",
    "edit_profile.btn.goal": "🎯 Objetivo",
    "edit_profile.btn.level": "🎓 Nivel",
    "edit_profile.btn.age": "🎂 Edad",
    "edit_profile.btn.size": "📏 Tamaño",
    "edit_profile.btn.timezone": "🌍 Zona horaria",
    "edit_profile.cancel.btn": "🔙 Cancelar",
    "edit_profile.level.1": "1 — No conoce comandos",
    "edit_profile.level.2": "2 — Conoce lo básico (sentado, parado)",
    "edit_profile.level.3": "3 — Obedece en casa",
    "edit_profile.level.4": "4 — Obedece con distracciones",
    "edit_profile.level.5": "5 — Excelentemente entrenado",
    "edit_profile.size.small": "Pequeño (hasta 10 kg)",
    "edit_profile.size.medium": "Mediano (10–25 kg)",
    "edit_profile.size.large": "Grande (25–45 kg)",
    "edit_profile.size.giant": "Gigante (45+ kg)",
    "edit_profile.age.1": "Cachorro (hasta 4 meses)",
    "edit_profile.age.2": "Cachorro (4–12 meses)",
    "edit_profile.age.3": "Joven (1–3 años)",
    "edit_profile.age.4": "Adulto (3–7 años)",
    "edit_profile.age.5": "Senior (7+ años)",
}
