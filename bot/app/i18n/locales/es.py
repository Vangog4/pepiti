"""Español/Mexicano (es) — Spanish (Latin America) translation."""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Pepito — Entrenador IA para perros</b>",
    "menu.main.choose": "Elige una sección:",
    "menu.btn.training": "🏋️ Entrenamiento de hoy",
    "menu.btn.week_plan": "📅 Plan semanal",
    "menu.btn.stats": "📊 Estadísticas",
    "menu.btn.coach": "💬 Pregunta al entrenador",
    "menu.btn.profile": "🐶 Mi mascota",
    "menu.btn.premium": "⭐ Obtener Premium",
    "menu.btn.premium.active": "⭐ Premium (activo)",
    "menu.btn.shop": "🛒 Tienda",
    "menu.btn.invite": "🐾 Invitar a un amigo",
    "menu.btn.webapp": "📊 Panel",
    "menu.main.streak": "{emoji} Entrenamientos completados: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "día",
    "menu.main.streak.days.few": "días",
    "menu.main.streak.days.many": "días",

    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 Menú principal",
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
    "settings.btn": "⚙️ Configuración",
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
        "🔄 <b>¿Generar un nuevo plan semanal?</b>\n\n"
        "Tu progreso semanal actual será reiniciado."
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
        "\n\n🎉 <b>¡{day} completado! ¡Excelente trabajo!</b>\n"
        "{emoji} Entrenamientos en total: {n}"
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
        "Gratis: <b>5 solicitudes IA por día</b>\n"
        "El límite se reinicia a la medianoche UTC.\n\n"
        "⭐ <b>Premium — ilimitado:</b>\n"
        "💬 Preguntas ilimitadas al entrenador\n"
        "🧠 Análisis detallado del progreso\n"
        "🎁 Recomendaciones personalizadas"
    ),
    "ai.rate_limit.btn": "⭐ Probar Premium",
    "ai.analyzing.premium": "🧠 <i>Realizando análisis detallado...</i>",
    "ai.analyzing.free": "🧠 <i>Analizando progreso...</i>",
    "ai.progress.premium.header": "⭐ <b>Análisis detallado para {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Análisis de progreso para {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 Volver a estadísticas",
    "ai.retry.btn": "🔄 Intentar de nuevo",
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
    "coach.new_thread.btn": "🆕 Nueva consulta",
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
    "referral.milestone.label.3":  "3 amigos",
    "referral.milestone.label.5":  "5 amigos",
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
    "premium.refunded": (
        "✔ Tu reembolso ha sido procesado. Suscripción Premium desactivada.\n"
        "Si esto es un error, por favor contacta al soporte."
    ),

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
    "reminder.disabled": (
        "🔕 <b>Desactivado</b>\n"
        "Ya no recibirás recordatorios diarios."
    ),
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
