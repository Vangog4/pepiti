"""Português Brasileiro (pt) — Brazilian Portuguese translation."""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Pepito — Treinador IA para cães</b>",
    "menu.main.choose": "Escolha uma seção:",
    "menu.btn.training": "🏋️ Treino de hoje",
    "menu.btn.week_plan": "📅 Plano semanal",
    "menu.btn.stats": "📊 Estatísticas",
    "menu.btn.coach": "💬 Perguntar ao treinador",
    "menu.btn.profile": "🐶 Meu pet",
    "menu.btn.premium": "⭐ Obter Premium",
    "menu.btn.premium.active": "⭐ Premium (ativo)",
    "menu.btn.shop": "🛒 Loja",
    "menu.btn.invite": "🐾 Convidar um amigo",
    "menu.btn.webapp": "📊 Painel",
    "menu.main.streak": "{emoji} Treinos concluídos: <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "dia",
    "menu.main.streak.days.few": "dias",
    "menu.main.streak.days.many": "dias",
    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 Menu principal",
    "common.back.btn": "🔙 Voltar",
    "common.menu.btn": "🔙 Menu",
    # ── Errors / Guards ────────────────────────────────────────────────────────
    "error.no_pet": "Por favor, complete o registro primeiro: /start",
    # ── Settings ───────────────────────────────────────────────────────────────
    "settings.main.title": "⚙️ <b>Configurações</b>",
    "settings.main.reminder_on": "⏰ Lembretes: <b>{time} ({tz})</b>",
    "settings.main.reminder_default": "⏰ Lembretes: <b>10:00 ({tz})</b> (padrão)",
    "settings.main.reminder_off": "⏰ Lembretes: <b>desativados</b>",
    "settings.language.title": "🌐 <b>Idioma</b>",
    "settings.language.choose": "Escolha o idioma da interface:",
    "settings.language.saved": "✅ Idioma alterado para <b>{name}</b>.",
    "settings.language.btn": "🌐 Idioma",
    "settings.btn": "⚙️ Configurações",
    "settings.reminder.btn": "⏰ Lembretes",
    # ── Onboarding (Stage 9: conversational AI) ────────────────────────────────
    "onboarding.start.returning": "Bem-vindo(a) de volta, {name}! 🐾\nO que faremos hoje?",
    "onboarding.ai.welcome": (
        "Olá, <b>{name}</b>! Eu sou o Pepito — seu treinador IA para cães. 🐶\n\n"
        "Fale sobre seu cão: nome, raça, idade e quais desafios vocês enfrentam?\n\n"
        "<i>Você pode escrever ou enviar uma mensagem de voz.</i>\n\n"
        "<b>Exemplo:</b> «Beagle Charlie, 2 anos, puxa a coleira e late para outros cães»"
    ),
    "onboarding.ai.thinking": "⏳ <i>Analisando...</i>",
    "onboarding.ai.photo_prompt": (
        "📷 Que pet lindo! Fale mais por texto ou voz:\n"
        "nome, raça, idade e com o que precisa de ajuda?"
    ),
    "onboarding.ai.clarify": "Anotado — <b>{summary}</b>\n\n{question}",
    "onboarding.ai.clarify.name": "Qual é o nome do seu pet?",
    "onboarding.ai.clarify.breed": "Qual é a raça?",
    "onboarding.ai.clarify.age_category": "Quantos anos tem? (filhote, jovem ou adulto?)",
    "onboarding.done.welcome": (
        "🎉 <b>Perfil criado!</b>\n\n"
        "Bem-vindo(a), {name}!\n"
        "Estou pronto para ajudá-lo(a) a treinar <b>{pet}</b>."
    ),
    "onboarding.done.referral_bonus": "\n\n🎁 <b>Bônus de indicação:</b> +{days} dias Premium ativados!",
    "onboarding.done.milestone": "\n🏆 <b>Marco de indicação:</b> {label} — {reward}!",
    "onboarding.done.plan_loading": "🐾 <i>Criando o primeiro plano de treinamento para {pet}...</i>",
    "onboarding.done.first_plan": "🏋️ <b>Aqui está seu primeiro plano!</b>\n\n{plan}",
    "onboarding.done.fallback": "Escolha por onde começar 👇",
    # ── Training ───────────────────────────────────────────────────────────────
    "training.loading": "🐾 <i>Criando um plano para {name}...</i>",
    "training.refresh.confirm": "🔄 <b>Gerar um novo plano?</b>\n\nSeu progresso atual será reiniciado.",
    "training.refresh.confirm.yes": "✅ Sim, novo plano",
    "training.refresh.confirm.no": "❌ Não",
    "training.refresh.loading": "🔄 <i>Gerando novo plano para {name}...</i>",
    "training.refresh.toast": "Gerando novo plano…",
    "training.week.loading": "📅 <i>Criando plano semanal para {name}...</i>",
    "training.week.refresh.confirm": (
        "🔄 <b>Gerar um novo plano semanal?</b>\n\nSeu progresso semanal atual será redefinido."
    ),
    "training.week.refresh.loading": "🔄 <i>Gerando novo plano semanal para {name}...</i>",
    "training.week.empty": (
        "📅 <b>Plano semanal</b>\n\n"
        "🌱 <b>Ainda sem tarefas</b>\n\n"
        "Comece com o plano diário — o Pepito criará o plano semanal "
        "assim que você tiver algum progresso!"
    ),
    "training.week.empty.cta.btn": "🏋️ Treino de hoje",
    "training.explain.btn": "📖 Explicar",
    "training.refresh.btn": "🔄 Novo plano",
    "training.explain.loading": "🔍 <i>Explicando o exercício «{title}»...</i>",
    "training.explain.back_daily.btn": "🔙 Voltar ao treino",
    "training.explain.back_weekly.btn": "🔙 Voltar ao plano",
    "training.task.not_found": "Tarefa não encontrada.",
    "training.plan.not_found": "Plano não encontrado.",
    "training.task.toggle.done": "✅ Concluído!",
    "training.task.toggle.undone": "↩️ Desfeito",
    "training.share.text": "{name} e eu treinamos {n} {days} seguidos com o Pepito! 🐾",
    "training.share.btn": "📤 Compartilhar",
    "training.done": (
        "\n\n🎉 <b>Treino concluído! Excelente trabalho!</b>\n{emoji} Treinos no total: {n}"
    ),
    "training.week_done": (
        "\n\n🎉 <b>{day} concluído! Excelente trabalho!</b>\n{emoji} Treinos no total: {n}"
    ),
    "training.stats.empty": (
        "🌱 <b>Você está apenas começando!</b>\n\n"
        "Sua primeira sessão é a mais importante.\n"
        "Abra o plano de hoje e marque o primeiro exercício como concluído — "
        "seu contador de treinos vai começar a crescer!"
    ),
    "training.stats.empty.cta": "🏋️ Começar treino",
    "training.minutes.abbr": "min",
    "training.goal.label": "Objetivo",
    "training.day.1": "Segunda-feira",
    "training.day.2": "Terça-feira",
    "training.day.3": "Quarta-feira",
    "training.day.4": "Quinta-feira",
    "training.day.5": "Sexta-feira",
    "training.day.6": "Sábado",
    "training.day.7": "Domingo",
    "training.day.short.1": "Se",
    "training.day.short.2": "Te",
    "training.day.short.3": "Qu",
    "training.day.short.4": "Qi",
    "training.day.short.5": "Sx",
    "training.day.short.6": "Sá",
    "training.day.short.7": "Do",
    "coach.display.photo": "[📷 Foto]",
    "coach.display.voice": "[🎤 Voz]",
    "coach.display.video": "[🎥 Vídeo]",
    "defaults.pet_name": "Animal",
    # ── AI / Coach ─────────────────────────────────────────────────────────────
    "ai.fallback": (
        "🧠 <b>O treinador está lidando com muitas solicitações agora</b>\n\n"
        "Tente novamente em um momento — isso geralmente se resolve rapidamente.\n"
        "<i>Se o problema persistir, digite /menu e tente novamente.</i>"
    ),
    "ai.rate_limit": (
        "💬 <b>Limite diário atingido</b>\n\n"
        "Gratuito: <b>5 solicitações IA por dia</b>\n"
        "O limite é redefinido à meia-noite UTC.\n\n"
        "⭐ <b>Premium — ilimitado:</b>\n"
        "💬 Perguntas ilimitadas ao treinador\n"
        "🧠 Análise detalhada do progresso\n"
        "🎁 Recomendações personalizadas"
    ),
    "ai.rate_limit.btn": "⭐ Experimentar Premium",
    "ai.analyzing.premium": "🧠 <i>Realizando análise detalhada...</i>",
    "ai.analyzing.free": "🧠 <i>Analisando progresso...</i>",
    "ai.progress.premium.header": "⭐ <b>Análise detalhada para {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Análise de progresso para {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 Voltar às estatísticas",
    "ai.retry.btn": "🔄 Tentar novamente",
    "ai.back_menu.btn": "🔙 Menu",
    "coach.entry": (
        "💬 <b>Pergunte ao treinador</b>\n\n"
        "Faça qualquer pergunta sobre treino ou comportamento — ou envie uma <b>📷 foto</b>.\n"
        "<i>Ex.: «Como parar de puxar a guia?» ou «Por que ele ignora o comando “Deita”?»</i>\n\n"
        "Gratuito: texto + foto\n"
        "⭐ Premium: + 🎤 mensagens de voz e 🎥 vídeos"
    ),
    "coach.thinking": "🧠 <i>Analisando sua pergunta...</i>",
    "coach.media.thinking": "🔍 <i>Analisando mídia...</i>",
    "coach.media.voice.premium": (
        "🎤 <b>Análise de voz — somente Premium</b>\n\n"
        "Envie uma <b>📷 foto</b> do seu cão — é gratuito.\n\n"
        "⭐ Premium desbloqueia análise de voz e vídeo sem limites."
    ),
    "coach.media.video.premium": (
        "🎥 <b>Análise de vídeo — somente Premium</b>\n\n"
        "Envie uma <b>📷 foto</b> do seu cão — é gratuito.\n\n"
        "⭐ Premium desbloqueia análise de vídeo e voz sem limites."
    ),
    "coach.media.too_large": "⚠️ Arquivo muito grande (máx 20 MB). Tente enviar um clipe mais curto.",
    "coach.hub.active_thread": (
        "💬 <b>Treinador</b> · <i>{title}</i>\n\n"
        "{count} mens. · em andamento\n\n"
        "Escreva uma pergunta ou envie uma foto."
    ),
    "coach.hub.archive_btn": "📁 Encerrar consulta",
    "coach.new_thread.btn": "🆕 Nova consulta",
    "coach.thread.archived": "✔ Consulta encerrada.",
    "coach.thread.title_default": "Consulta",
    "coach.role.owner": "Dono",
    "coach.role.trainer": "Treinador",
    "coach.summary.header": "Breve resumo da conversa anterior:",
    # ── Voice-action (hands-free task reporting) ───────────────────────────────
    "voice_action.thinking": "🐾 <i>Analisando...</i>",
    "voice_action.marked": "✅ Marquei a tarefa <b>{task}</b> como concluída!\n\n",
    "voice_action.all_done": "🎉 Todas as tarefas do dia concluídas! Ótimo treino!",
    # ── Stats ──────────────────────────────────────────────────────────────────
    "stats.header": "📊 <b>Estatísticas de {name}</b>\n\n",
    "stats.days_with_us": "🗓 Dias com o Pepito: <b>{n}</b>\n",
    "stats.completed": "{emoji} Sessões concluídas: <b>{n}</b>\n\n",
    "stats.level": "🏆 Nível de obediência: <b>{level}</b>\n\n",
    "stats.motivate": "<i>Cada sessão torna {name} melhor!</i> 🚀",
    "stats.analysis.premium.btn": "🧠 Análise IA detalhada ⭐",
    "stats.analysis.free.btn": "🧠 Análise IA de progresso",
    # ── Profile ────────────────────────────────────────────────────────────────
    "profile.header": "🐾 <b>{name}</b>\n\n",
    "profile.breed": "🐕 Raça: {val}\n",
    "profile.sex": "⚥ Sexo: {val}\n",
    "profile.age": "🎂 Idade: {val}\n",
    "profile.size": "📏 Tamanho: {val}\n",
    "profile.weight": "⚖️ Peso: {val}\n\n",
    "profile.level": "🎓 Nível: {val}/5\n",
    "profile.goal": "🎯 Objetivo: {val}\n",
    "profile.issues": "📋 Problemas: {val}\n",
    "profile.schedule": "🗓 Agenda: {val}\n\n",
    "profile.training_count": "🔥 Sessões concluídas: <b>{n}</b>",
    "profile.weight.unit": "kg",
    "profile.weight.unknown": "não especificado",
    "profile.issues.none": "nenhum",
    "profile.schedule.unknown": "não especificado",
    "profile.edit.btn": "✏️ Editar perfil",
    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>Loja PepitoPet</b>",
    "shop.body": (
        "Petiscos naturais artesanais — "
        "sem aditivos ou conservantes, apenas carne real.\n\n"
        "Escolha uma categoria:"
    ),
    "shop.cat.training.btn": "🎯 Petiscos de treino",
    "shop.cat.longplay.btn": "🦴 Mastigáveis de longa duração",
    "shop.cat.by_size.btn": "🐶 Filhotes & por tamanho",
    "shop.cat.all.btn": "🛒 Loja completa",
    "shop.rec.puppy_named": "🐶 Petiscos para filhotes — para {name}",
    "shop.rec.small_named": "🐶 Petiscos para raças pequenas — para {name}",
    "shop.rec.puppy_small_free": "🐶 Petiscos para filhotes e cães pequenos",
    "shop.rec.longplay_named": "🎁 Petiscos duradouros — recompensa para {name}",
    "shop.rec.longplay_free": "🦴 Petiscos duradouros",
    "shop.rec.exercise_named": "🦴 Petiscos de exercício para {name}",
    "shop.rec.training_named": "🦴 Petiscos de treino para {name}",
    "shop.rec.training_free": "🦴 Petiscos de treino",
    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>Convide um amigo — bônus para os dois!</b>",
    "invite.link_label": "🔗 Seu link:",
    "invite.bonus": "🎁 Cada amigo dá <b>+{days} dias Premium</b> — para você <i>e</i> para ele.",
    "invite.ladder.title": "🏆 <b>Caminho de recompensas:</b>",
    "invite.count": "👥 Convidados: <b>{n}</b>",
    "invite.next": "🎯 Até a próxima recompensa: mais <b>{n}</b>",
    "invite.all_done": "👑 <b>Todas as recompensas obtidas! Você é uma lenda!</b>",
    "invite.share.btn": "📤 Compartilhar link",
    "invite.share.text": "Treino meu pet com Pepito treinador IA 🐾",
    "invite.base_tier": "1 amigo    — +{days} dias Premium (para os dois)",
    "invite.goal": "🎯 Mais {needed} para {next_label} ({reward})",
    "invite.current_goal": "← próximo objetivo",
    "invite.how.title": "❓ <b>Como funciona:</b>",
    "invite.how.1": "1. Compartilhe seu link",
    "invite.how.2": "2. O amigo inicia o bot e preenche o perfil",
    "invite.how.3": "3. Vocês dois recebem +{days} dias Premium",
    # ── Referral push-notifications ────────────────────────────────────────────
    "referral.notify.base": (
        "🎉 Um novo amigo entrou pelo seu link!\n"
        "+{days} dias Premium adicionados. Convidados: <b>{count}</b>\n{ladder_hint}"
    ),
    "referral.notify.milestone": (
        "🏆 <b>{label}!</b>\n\nVocê convidou {count} amigos e ganha <b>{reward}</b>!\n{next_hint}"
    ),
    "referral.notify.next_hint": "🎯 Próximo objetivo: {next_label} → {next_reward}",
    "referral.notify.all_done": "👑 Todas as recompensas desbloqueadas!",
    "referral.milestone.label.3": "3 amigos",
    "referral.milestone.label.5": "5 amigos",
    "referral.milestone.label.10": "10 amigos",
    "referral.milestone.label.25": "25 amigos",
    "referral.reward.days": "+{days} dias",
    # ── Premium / Subscription ─────────────────────────────────────────────────
    "premium.active.title": "⭐ <b>Premium ativo</b>",
    "premium.active.expires": "Válido até: <b>{date}</b>",
    "premium.active.features": (
        "\n\nIncluído:\n"
        "💬 Perguntas ilimitadas ao treinador\n"
        "🧠 Análise IA detalhada do progresso\n"
        "🎁 Recomendações de petiscos personalizadas"
    ),
    "premium.upsell.body": (
        "⭐ <b>Pepito Premium</b>\n\n"
        "💬 Perguntas ao treinador — sem limites\n"
        "🧠 Análise IA detalhada do progresso\n"
        "🎁 Recomendações personalizadas de petiscos\n\n"
        "<b>{price} Stars</b> / mês · ou convide 3 amigos — grátis"
    ),
    "premium.upsell.btn": "⭐ Obter Premium por {price} Stars",
    "premium.invoice.title": "Pepito Premium — 1 mês",
    "premium.invoice.description": "Treinador IA ilimitado, relatórios detalhados e análise comportamental profunda.",
    "premium.invoice.label": "Premium 1 mês",
    "premium.activated": (
        "🎉 <b>Premium ativado!</b>\n\n"
        "Agora disponível:\n"
        "💬 Perguntas ilimitadas ao treinador\n"
        "🧠 Análise detalhada do progresso\n"
        "🎁 Recomendações de petiscos personalizadas\n\n"
        "Use /menu para começar."
    ),
    "premium.refunded": (
        "✔ Seu reembolso foi processado. Assinatura Premium desativada.\n"
        "Se isso for um erro, entre em contato com o suporte."
    ),
    "webapp.validation.name_empty": "O nome não pode estar vazio",
    "webapp.validation.name_long": "Nome: no máximo 30 caracteres",
    "webapp.validation.breed_long": "Raça: no máximo 40 caracteres",
    "webapp.validation.goal_long": "Objetivo: no máximo 150 caracteres",
    "webapp.validation.level": "Nível de treino inválido",
    "webapp.validation.age": "Categoria de idade inválida",
    "webapp.validation.reminder": "Formato: HH:MM, ex. 09:30",
    "webapp.validation.timezone": "Fuso horário inválido",
    "webapp.validation.language": "Idioma inválido",
    # ── Reminders ─────────────────────────────────────────────────────────────
    "reminder.title": "⏰ <b>Lembretes</b>",
    "reminder.status.off": "🔕 <b>Desativado</b>",
    "reminder.status.off.desc": "Os lembretes diários não estão ativos.",
    "reminder.status.on": "🔔 <b>Ativado</b> — {time} ({tz}) todo dia",
    "reminder.status.default": "🔔 <b>Ativado</b> — 10:00 ({tz}, padrão)",
    "reminder.status.on.desc": "O Pepito vai te lembrar de treinar seu pet.",
    "reminder.input.prompt": (
        "⏰ <b>Lembretes</b>\n\n"
        "Digite o horário no formato <code>HH:MM</code> no seu fuso horário (<b>{tz}</b>).\n"
        "Exemplos: <code>09:00</code>, <code>18:30</code>\n\n"
        "<i>Você pode alterar seu fuso horário em ✏️ Editar perfil → 🌍 Fuso horário.</i>"
    ),
    "reminder.disabled": ("🔕 <b>Desativado</b>\nVocê não receberá mais lembretes diários."),
    "reminder.saved": "✅ <b>Pronto!</b> Lembrete definido para <b>{time} ({tz})</b> todo dia.",
    "reminder.error.format": (
        "⚠️ Formato inválido. Digite o horário como <code>HH:MM</code>, ex. <code>09:30</code>."
    ),
    "reminder.enable.btn": "🔔 Ativar lembretes",
    "reminder.change.btn": "✏️ Alterar horário",
    "reminder.disable.btn": "🔕 Desativar",
    "reminder.back.btn": "🔙 Voltar aos lembretes",
    "reminder.back_settings.btn": "🔙 Voltar",
    "reminder.settings.btn": "⏰ Configurações de lembretes",
    "reminder.menu.btn": "🔙 Menu",
    "reminder.tz_missing": "⚠️ <b>Fuso horário não definido</b> — usando UTC+0. Defina-o para que os lembretes cheguem na hora certa.",
    "reminder.tz_change.btn": "🌍 Definir fuso horário",
    "reminder.push.friend": "amigo",
    "reminder.push.text": "🐾 Olá, {name}!\n\nNão esqueça de treinar com seu pet hoje. Abra /menu para ver o plano.",
    "report.weekly.premium": (
        "📊 Relatório semanal, {name}!\n\n"
        "Total de dias de treino: <b>{days}</b>\n"
        "Continue assim! Abra /menu para detalhes."
    ),
    "report.weekly.free": (
        "📊 Resumo semanal, {name}!\n\n"
        "Dias de treino: <b>{days}</b>\n"
        "Obtenha análises detalhadas com Premium — /menu."
    ),
    # ── Help / Support ─────────────────────────────────────────────────────────
    "help.guide.title": "❓ <b>Guia do Pepito</b>\n\n",
    "help.guide.plan.header": "🧠 <b>Como funcionam os planos de treino</b>\n",
    "help.guide.plan.text": (
        "O Pepito gera um plano todo dia baseado no perfil do seu pet. "
        "Toque em «🏋️ Treino de hoje» para ver sua lista de tarefas.\n\n"
    ),
    "help.guide.streak.header": "✅ <b>Caixas de seleção & progresso</b>\n",
    "help.guide.streak.text": (
        "Marque ○ → ✅ cada exercício. Complete todas as tarefas e o dia conta — "
        "seu total de treinos cresce.\n\n"
    ),
    "help.guide.shop.header": "🛍️ <b>Loja & recompensas</b>\n",
    "help.guide.shop.text": (
        "Após o treino o Pepito recomenda petiscos naturais PepitoPet. "
        "Convide amigos — ganhe bônus: +30, +60, +90 e +180 dias Premium nos marcos.\n\n"
    ),
    "help.guide.premium.header": "⭐ <b>O que o Premium oferece</b>\n",
    "help.guide.premium.text": (
        "💬 Perguntas ilimitadas ao treinador\n"
        "🧠 Análise IA detalhada do progresso\n"
        "🎁 Recomendações personalizadas com o nome do seu pet\n\n"
    ),
    "help.guide.commands": "<b>Comandos:</b> /menu · /start · /reset",
    "help.support.btn": "💬 Contatar suporte",
    "help.btn": "❓ Ajuda",
    "help.back_settings.btn": "🔙 Voltar às configurações",
    # ── Edit Profile ───────────────────────────────────────────────────────────
    "edit_profile.title": "✏️ <b>Editar perfil</b>\n\nO que deseja alterar?",
    "edit_profile.field.name.prompt": "Digite o novo nome do pet no chat:",
    "edit_profile.field.breed.prompt": "Digite a nova raça no chat:",
    "edit_profile.field.goal.prompt": "Escreva o novo objetivo de treinamento no chat:",
    "edit_profile.field.level.prompt": "Escolha o novo nível de obediência:",
    "edit_profile.field.age.prompt": "Escolha a nova categoria de idade:",
    "edit_profile.field.size.prompt": "Escolha o novo tamanho do pet:",
    "edit_profile.field.timezone.prompt": "🌍 Escolha seu fuso horário:",
    "edit_profile.saved": "✅ Atualizado: <b>{value}</b>",
    "edit_profile.edit_more.btn": "✏️ Editar mais",
    "edit_profile.error.empty": "⚠️ O campo não pode estar vazio. Tente novamente.",
    "edit_profile.error.too_long": "⚠️ Valor muito longo — máximo 50 caracteres (o seu: {n}).",
    "edit_profile.btn.name": "🐾 Nome",
    "edit_profile.btn.breed": "🐕 Raça",
    "edit_profile.btn.goal": "🎯 Objetivo",
    "edit_profile.btn.level": "🎓 Nível",
    "edit_profile.btn.age": "🎂 Idade",
    "edit_profile.btn.size": "📏 Tamanho",
    "edit_profile.btn.timezone": "🌍 Fuso horário",
    "edit_profile.cancel.btn": "🔙 Cancelar",
    "edit_profile.level.1": "1 — Não conhece comandos",
    "edit_profile.level.2": "2 — Conhece o básico (sentar, ficar)",
    "edit_profile.level.3": "3 — Obedece em casa",
    "edit_profile.level.4": "4 — Obedece com distrações",
    "edit_profile.level.5": "5 — Excelentemente treinado",
    "edit_profile.size.small": "Pequeno (até 10 kg)",
    "edit_profile.size.medium": "Médio (10–25 kg)",
    "edit_profile.size.large": "Grande (25–45 kg)",
    "edit_profile.size.giant": "Gigante (45+ kg)",
    "edit_profile.age.1": "Filhote (até 4 meses)",
    "edit_profile.age.2": "Filhote (4–12 meses)",
    "edit_profile.age.3": "Jovem (1–3 anos)",
    "edit_profile.age.4": "Adulto (3–7 anos)",
    "edit_profile.age.5": "Sênior (7+ anos)",
}
