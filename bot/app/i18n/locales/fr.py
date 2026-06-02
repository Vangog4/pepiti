"""Français (fr) — French translation."""

STRINGS: dict[str, str] = {
    # ── Main menu ──────────────────────────────────────────────────────────────
    "menu.main.greeting": "🐾 <b>Pepito — Coach IA pour chiens</b>",
    "menu.main.choose": "Choisissez une section :",
    "menu.btn.training": "🏋️ Entraînement du jour",
    "menu.btn.week_plan": "📅 Plan hebdomadaire",
    "menu.btn.stats": "📊 Statistiques",
    "menu.btn.coach": "💬 Demander au coach",
    "menu.btn.profile": "🐶 Mon animal",
    "menu.btn.premium": "⭐ Obtenir Premium",
    "menu.btn.premium.active": "⭐ Premium (actif)",
    "menu.btn.shop": "🛒 Boutique",
    "menu.btn.invite": "🐾 Inviter un ami",
    "menu.btn.webapp": "📊 Tableau de bord",
    "menu.main.streak": "{emoji} Entraînements effectués : <b>{n}</b>\n\n",
    "menu.main.streak.days.one": "jour",
    "menu.main.streak.days.few": "jours",
    "menu.main.streak.days.many": "jours",
    # ── Common buttons ─────────────────────────────────────────────────────────
    "common.back_menu.btn": "🔙 Menu principal",
    "common.back.btn": "🔙 Retour",
    "common.menu.btn": "🔙 Menu",
    # ── Errors / Guards ────────────────────────────────────────────────────────
    "error.no_pet": "Veuillez d'abord compléter l'inscription : /start",
    # ── Settings ───────────────────────────────────────────────────────────────
    "settings.main.title": "⚙️ <b>Paramètres</b>",
    "settings.main.reminder_on": "⏰ Rappels : <b>{time} ({tz})</b>",
    "settings.main.reminder_default": "⏰ Rappels : <b>10:00 ({tz})</b> (par défaut)",
    "settings.main.reminder_off": "⏰ Rappels : <b>désactivés</b>",
    "settings.language.title": "🌐 <b>Langue</b>",
    "settings.language.choose": "Choisissez la langue de l'interface :",
    "settings.language.saved": "✅ Langue changée en <b>{name}</b>.",
    "settings.language.btn": "🌐 Langue",
    "settings.btn": "⚙️ Paramètres",
    "settings.reminder.btn": "⏰ Rappels",
    # ── Onboarding (Stage 9: conversational AI) ────────────────────────────────
    "onboarding.start.returning": "Bon retour, {name} ! 🐾\nQue faisons-nous aujourd'hui ?",
    "onboarding.ai.welcome": (
        "Bonjour, <b>{name}</b> ! Je suis Pepito — votre coach IA pour chiens. 🐶\n\n"
        "Parlez-moi de votre chien : nom, race, âge et quels défis rencontrez-vous ?\n\n"
        "<i>Vous pouvez écrire ou envoyer un message vocal.</i>\n\n"
        "<b>Exemple :</b> «Beagle Charlie, 2 ans, tire sur la laisse et aboie sur les autres chiens»"
    ),
    "onboarding.ai.thinking": "⏳ <i>Analyse en cours...</i>",
    "onboarding.ai.photo_prompt": (
        "📷 Bel animal ! Parlez-moi de lui par écrit ou vocal :\n"
        "nom, race, âge et en quoi avez-vous besoin d'aide ?"
    ),
    "onboarding.ai.clarify": "Noté — <b>{summary}</b>\n\n{question}",
    "onboarding.ai.clarify.name": "Quel est le nom de votre animal ?",
    "onboarding.ai.clarify.breed": "Quelle est sa race ?",
    "onboarding.ai.clarify.age_category": "Quel âge a-t-il ? (chiot, jeune ou adulte ?)",
    "onboarding.done.welcome": (
        "🎉 <b>Profil créé !</b>\n\n"
        "Bienvenue, {name} !\n"
        "Je suis prêt à vous aider à entraîner <b>{pet}</b>."
    ),
    "onboarding.done.referral_bonus": "\n\n🎁 <b>Bonus de parrainage :</b> +{days} jours Premium activés !",
    "onboarding.done.milestone": "\n🏆 <b>Jalon de parrainage :</b> {label} — {reward} !",
    "onboarding.done.plan_loading": "🐾 <i>Création du premier plan d'entraînement pour {pet}...</i>",
    "onboarding.done.first_plan": "🏋️ <b>Voici votre premier plan !</b>\n\n{plan}",
    "onboarding.done.fallback": "Choisissez par où commencer 👇",
    # ── Training ───────────────────────────────────────────────────────────────
    "training.loading": "🐾 <i>Création d'un plan pour {name}...</i>",
    "training.refresh.confirm": "🔄 <b>Générer un nouveau plan ?</b>\n\nVotre progression actuelle sera réinitialisée.",
    "training.refresh.confirm.yes": "✅ Oui, nouveau plan",
    "training.refresh.confirm.no": "❌ Non",
    "training.refresh.loading": "🔄 <i>Génération d'un nouveau plan pour {name}...</i>",
    "training.refresh.toast": "Génération du nouveau plan…",
    "training.week.loading": "📅 <i>Création d'un plan hebdomadaire pour {name}...</i>",
    "training.week.refresh.confirm": (
        "🔄 <b>Générer un nouveau plan hebdomadaire ?</b>\n\n"
        "Votre progression hebdomadaire actuelle sera réinitialisée."
    ),
    "training.week.refresh.loading": "🔄 <i>Génération d'un nouveau plan hebdomadaire pour {name}...</i>",
    "training.week.empty": (
        "📅 <b>Plan hebdomadaire</b>\n\n"
        "🌱 <b>Pas encore de tâches</b>\n\n"
        "Commencez par le plan quotidien — Pepito créera le plan hebdomadaire "
        "une fois que vous aurez un peu de progression !"
    ),
    "training.week.empty.cta.btn": "🏋️ Entraînement du jour",
    "training.explain.btn": "📖 Expliquer",
    "training.refresh.btn": "🔄 Nouveau plan",
    "training.explain.loading": "🔍 <i>Explication de l'exercice «{title}»...</i>",
    "training.explain.back_daily.btn": "🔙 Retour à l'entraînement",
    "training.explain.back_weekly.btn": "🔙 Retour au plan",
    "training.task.not_found": "Tâche introuvable.",
    "training.plan.not_found": "Plan introuvable.",
    "training.task.toggle.done": "✅ Fait !",
    "training.task.toggle.undone": "↩️ Annulé",
    "training.share.text": "{name} et moi avons entraîné {n} {days} de suite avec Pepito ! 🐾",
    "training.share.btn": "📤 Partager",
    "training.done": (
        "\n\n🎉 <b>Entraînement terminé ! Bravo !</b>\n{emoji} Entraînements au total : {n}"
    ),
    "training.week_done": (
        "\n\n🎉 <b>{day} terminé ! Bravo !</b>\n{emoji} Entraînements au total : {n}"
    ),
    "training.stats.empty": (
        "🌱 <b>Vous débutez tout juste !</b>\n\n"
        "Votre première séance est la plus importante.\n"
        "Ouvrez le plan du jour et marquez le premier exercice comme terminé — "
        "votre compteur d'entraînements commencera à croître !"
    ),
    "training.stats.empty.cta": "🏋️ Commencer l'entraînement",
    "training.minutes.abbr": "min",
    "training.goal.label": "Objectif",
    "training.day.1": "Lundi",
    "training.day.2": "Mardi",
    "training.day.3": "Mercredi",
    "training.day.4": "Jeudi",
    "training.day.5": "Vendredi",
    "training.day.6": "Samedi",
    "training.day.7": "Dimanche",
    "training.day.short.1": "Lu",
    "training.day.short.2": "Ma",
    "training.day.short.3": "Me",
    "training.day.short.4": "Je",
    "training.day.short.5": "Ve",
    "training.day.short.6": "Sa",
    "training.day.short.7": "Di",
    "coach.display.photo": "[📷 Photo]",
    "coach.display.voice": "[🎤 Vocal]",
    "coach.display.video": "[🎥 Vidéo]",
    "defaults.pet_name": "Animal",
    # ── AI / Coach ─────────────────────────────────────────────────────────────
    "ai.fallback": (
        "🧠 <b>Le coach traite trop de demandes en ce moment</b>\n\n"
        "Réessayez dans un instant — cela se résout généralement rapidement.\n"
        "<i>Si le problème persiste, tapez /menu et réessayez.</i>"
    ),
    "ai.rate_limit": (
        "💬 <b>Limite quotidienne atteinte</b>\n\n"
        "Gratuit : <b>5 requêtes IA par jour</b>\n"
        "La limite se réinitialise à minuit UTC.\n\n"
        "⭐ <b>Premium — illimité :</b>\n"
        "💬 Questions illimitées au coach\n"
        "🧠 Analyse approfondie de la progression\n"
        "🎁 Recommandations personnalisées"
    ),
    "ai.rate_limit.btn": "⭐ Essayer Premium",
    "ai.analyzing.premium": "🧠 <i>Analyse approfondie en cours...</i>",
    "ai.analyzing.free": "🧠 <i>Analyse de la progression...</i>",
    "ai.progress.premium.header": "⭐ <b>Analyse approfondie pour {name}</b>\n\n",
    "ai.progress.free.header": "📈 <b>Analyse de progression pour {name}</b>\n\n",
    "ai.progress.back.btn": "🔙 Retour aux stats",
    "ai.retry.btn": "🔄 Réessayer",
    "ai.back_menu.btn": "🔙 Menu",
    "coach.entry": (
        "💬 <b>Demander au coach</b>\n\n"
        "Posez n'importe quelle question sur le dressage ou le comportement — ou envoyez une <b>📷 photo</b>.\n"
        "<i>Ex. : «Comment arrêter de tirer sur la laisse ?» ou «Pourquoi ignore-t-il “Couché” ?»</i>\n\n"
        "Gratuit : texte + photo\n"
        "⭐ Premium : + 🎤 messages vocaux et 🎥 vidéos"
    ),
    "coach.thinking": "🧠 <i>Analyse de votre question...</i>",
    "coach.media.thinking": "🔍 <i>Analyse des médias...</i>",
    "coach.media.voice.premium": (
        "🎤 <b>Analyse vocale — Premium uniquement</b>\n\n"
        "Envoyez une <b>📷 photo</b> de votre chien — c'est gratuit.\n\n"
        "⭐ Premium débloque l'analyse vocale et vidéo sans limites."
    ),
    "coach.media.video.premium": (
        "🎥 <b>Analyse vidéo — Premium uniquement</b>\n\n"
        "Envoyez une <b>📷 photo</b> de votre chien — c'est gratuit.\n\n"
        "⭐ Premium débloque l'analyse vidéo et vocale sans limites."
    ),
    "coach.media.too_large": "⚠️ Fichier trop volumineux (max 20 Mo). Essayez un clip plus court.",
    "coach.hub.active_thread": (
        "💬 <b>Coach</b> · <i>{title}</i>\n\n"
        "{count} msg · en cours\n\n"
        "Posez une question ou envoyez une photo."
    ),
    "coach.hub.archive_btn": "📁 Terminer la consultation",
    "coach.new_thread.btn": "🆕 Nouvelle consultation",
    "coach.thread.archived": "✔ Consultation terminée.",
    "coach.thread.title_default": "Consultation",
    "coach.role.owner": "Propriétaire",
    "coach.role.trainer": "Coach",
    "coach.summary.header": "Bref résumé de la conversation précédente :",
    # ── Voice-action (hands-free task reporting) ───────────────────────────────
    "voice_action.thinking": "🐾 <i>Analyse en cours...</i>",
    "voice_action.marked": "✅ J'ai marqué la tâche <b>{task}</b> comme accomplie !\n\n",
    "voice_action.all_done": "🎉 Toutes les tâches du jour accomplies ! Excellent entraînement !",
    # ── Stats ──────────────────────────────────────────────────────────────────
    "stats.header": "📊 <b>Statistiques de {name}</b>\n\n",
    "stats.days_with_us": "🗓 Jours avec Pepito : <b>{n}</b>\n",
    "stats.completed": "{emoji} Séances terminées : <b>{n}</b>\n\n",
    "stats.level": "🏆 Niveau d'obéissance : <b>{level}</b>\n\n",
    "stats.motivate": "<i>Chaque séance améliore {name} !</i> 🚀",
    "stats.analysis.premium.btn": "🧠 Analyse IA approfondie ⭐",
    "stats.analysis.free.btn": "🧠 Analyse IA de progression",
    # ── Profile ────────────────────────────────────────────────────────────────
    "profile.header": "🐾 <b>{name}</b>\n\n",
    "profile.breed": "🐕 Race : {val}\n",
    "profile.sex": "⚥ Sexe : {val}\n",
    "profile.age": "🎂 Âge : {val}\n",
    "profile.size": "📏 Taille : {val}\n",
    "profile.weight": "⚖️ Poids : {val}\n\n",
    "profile.level": "🎓 Niveau : {val}/5\n",
    "profile.goal": "🎯 Objectif : {val}\n",
    "profile.issues": "📋 Problèmes : {val}\n",
    "profile.schedule": "🗓 Planning : {val}\n\n",
    "profile.training_count": "🔥 Séances terminées : <b>{n}</b>",
    "profile.weight.unit": "kg",
    "profile.weight.unknown": "non spécifié",
    "profile.issues.none": "aucun",
    "profile.schedule.unknown": "non spécifié",
    "profile.edit.btn": "✏️ Modifier le profil",
    # ── Shop ───────────────────────────────────────────────────────────────────
    "shop.title": "🛒 <b>Boutique PepitoPet</b>",
    "shop.body": (
        "Friandises naturelles maison — "
        "sans additifs ni conservateurs, uniquement de la vraie viande.\n\n"
        "Choisissez une catégorie :"
    ),
    "shop.cat.training.btn": "🎯 Friandises d'entraînement",
    "shop.cat.longplay.btn": "🦴 Mâchouilles longue durée",
    "shop.cat.by_size.btn": "🐶 Chiots & par taille",
    "shop.cat.all.btn": "🛒 Toute la boutique",
    # ── Invite / Referral ──────────────────────────────────────────────────────
    "invite.title": "🐾 <b>Invitez un ami — bonus pour tous les deux !</b>",
    "invite.link_label": "🔗 Votre lien :",
    "invite.bonus": "🎁 Chaque ami donne <b>+{days} jours Premium</b> — à vous <i>et</i> à lui.",
    "invite.ladder.title": "🏆 <b>Chemin de récompenses :</b>",
    "invite.count": "👥 Invités : <b>{n}</b>",
    "invite.next": "🎯 Jusqu'à la prochaine récompense : encore <b>{n}</b>",
    "invite.all_done": "👑 <b>Toutes les récompenses obtenues ! Vous êtes une légende !</b>",
    "invite.share.btn": "📤 Partager le lien",
    "invite.share.text": "J'entraîne mon animal avec Pepito coach IA 🐾",
    "invite.base_tier": "1 ami      — +{days} jours Premium (pour les deux)",
    "invite.goal": "🎯 Encore {needed} pour {next_label} ({reward})",
    "invite.current_goal": "← prochain objectif",
    "invite.how.title": "❓ <b>Comment ça marche :</b>",
    "invite.how.1": "1. Partagez votre lien",
    "invite.how.2": "2. L'ami lance le bot et remplit son profil",
    "invite.how.3": "3. Vous recevez tous les deux +{days} jours Premium",
    # ── Referral push-notifications ────────────────────────────────────────────
    "referral.notify.base": (
        "🎉 Un nouvel ami a rejoint via votre lien !\n"
        "+{days} jours Premium ajoutés. Amis invités : <b>{count}</b>\n{ladder_hint}"
    ),
    "referral.notify.milestone": (
        "🏆 <b>{label} !</b>\n\n"
        "Vous avez invité {count} amis et gagnez <b>{reward}</b> !\n{next_hint}"
    ),
    "referral.notify.next_hint": "🎯 Prochain objectif : {next_label} → {next_reward}",
    "referral.notify.all_done": "👑 Toutes les récompenses débloquées !",
    "referral.milestone.label.3": "3 amis",
    "referral.milestone.label.5": "5 amis",
    "referral.milestone.label.10": "10 amis",
    "referral.milestone.label.25": "25 amis",
    "referral.reward.days": "+{days} jours",
    # ── Premium / Subscription ─────────────────────────────────────────────────
    "premium.active.title": "⭐ <b>Premium actif</b>",
    "premium.active.expires": "Valide jusqu'au : <b>{date}</b>",
    "premium.active.features": (
        "\n\nInclus :\n"
        "💬 Questions illimitées au coach\n"
        "🧠 Analyse IA approfondie de la progression\n"
        "🎁 Recommandations de friandises personnalisées"
    ),
    "premium.upsell.body": (
        "⭐ <b>Pepito Premium</b>\n\n"
        "💬 Questions au coach — sans limite\n"
        "🧠 Analyse IA approfondie de la progression\n"
        "🎁 Recommandations personnalisées de friandises\n\n"
        "<b>{price} Stars</b> / mois · ou invite 3 amis — gratuit"
    ),
    "premium.upsell.btn": "⭐ Obtenir Premium pour {price} Stars",
    "premium.invoice.title": "Pepito Premium — 1 mois",
    "premium.invoice.description": "Coach IA illimité, rapports détaillés et analyse comportementale approfondie.",
    "premium.invoice.label": "Premium 1 mois",
    "premium.activated": (
        "🎉 <b>Premium activé !</b>\n\n"
        "Maintenant disponible :\n"
        "💬 Questions illimitées au coach\n"
        "🧠 Analyse approfondie de la progression\n"
        "🎁 Recommandations de friandises personnalisées\n\n"
        "Utilisez /menu pour commencer."
    ),
    "premium.refunded": (
        "✔ Votre remboursement a été traité. Abonnement Premium désactivé.\n"
        "Si c'est une erreur, veuillez contacter le support."
    ),
    # ── Reminders ─────────────────────────────────────────────────────────────
    "reminder.title": "⏰ <b>Rappels</b>",
    "reminder.status.off": "🔕 <b>Désactivé</b>",
    "reminder.status.off.desc": "Les rappels quotidiens ne sont pas actifs.",
    "reminder.status.on": "🔔 <b>Activé</b> — {time} ({tz}) chaque jour",
    "reminder.status.default": "🔔 <b>Activé</b> — 10:00 ({tz}, par défaut)",
    "reminder.status.on.desc": "Pepito vous rappellera d'entraîner votre animal.",
    "reminder.input.prompt": (
        "⏰ <b>Rappels</b>\n\n"
        "Entrez l'heure au format <code>HH:MM</code> dans votre fuseau horaire (<b>{tz}</b>).\n"
        "Exemples : <code>09:00</code>, <code>18:30</code>\n\n"
        "<i>Vous pouvez changer votre fuseau horaire dans ✏️ Modifier le profil → 🌍 Fuseau horaire.</i>"
    ),
    "reminder.disabled": ("🔕 <b>Désactivé</b>\nVous ne recevrez plus de rappels quotidiens."),
    "reminder.saved": "✅ <b>Fait !</b> Rappel défini pour <b>{time} ({tz})</b> chaque jour.",
    "reminder.error.format": (
        "⚠️ Format invalide. Entrez l'heure comme <code>HH:MM</code>, ex. <code>09:30</code>."
    ),
    "reminder.enable.btn": "🔔 Activer les rappels",
    "reminder.change.btn": "✏️ Changer l'heure",
    "reminder.disable.btn": "🔕 Désactiver",
    "reminder.back.btn": "🔙 Retour aux rappels",
    "reminder.back_settings.btn": "🔙 Retour",
    "reminder.settings.btn": "⏰ Paramètres des rappels",
    "reminder.menu.btn": "🔙 Menu",
    "reminder.tz_missing": "⚠️ <b>Fuseau horaire non défini</b> — UTC+0 est utilisé. Définis-le pour recevoir les rappels au bon moment.",
    "reminder.tz_change.btn": "🌍 Définir le fuseau horaire",
    "reminder.push.friend": "ami",
    "reminder.push.text": "🐾 Salut, {name} !\n\nN'oublie pas d'entraîner ton animal aujourd'hui. Ouvre /menu pour voir le plan.",
    "report.weekly.premium": (
        "📊 Rapport hebdomadaire, {name} !\n\n"
        "Total des jours d'entraînement : <b>{days}</b>\n"
        "Continue comme ça ! Ouvre /menu pour les détails."
    ),
    "report.weekly.free": (
        "📊 Bilan de la semaine, {name} !\n\n"
        "Jours d'entraînement : <b>{days}</b>\n"
        "Obtiens des analyses détaillées avec Premium — /menu."
    ),
    # ── Help / Support ─────────────────────────────────────────────────────────
    "help.guide.title": "❓ <b>Guide Pepito</b>\n\n",
    "help.guide.plan.header": "🧠 <b>Comment fonctionnent les plans d'entraînement</b>\n",
    "help.guide.plan.text": (
        "Pepito génère un plan chaque jour basé sur le profil de votre animal. "
        "Appuyez sur «🏋️ Entraînement du jour» pour votre liste de tâches.\n\n"
    ),
    "help.guide.streak.header": "✅ <b>Cases à cocher & progrès</b>\n",
    "help.guide.streak.text": (
        "Marquez ○ → ✅ chaque exercice. Complétez toutes les tâches et le jour compte — "
        "votre total d'entraînements augmente.\n\n"
    ),
    "help.guide.shop.header": "🛍️ <b>Boutique & récompenses</b>\n",
    "help.guide.shop.text": (
        "Après l'entraînement, Pepito recommande des friandises naturelles PepitoPet. "
        "Invitez des amis — gagnez des bonus : +30, +60, +90 et +180 jours Premium aux jalons.\n\n"
    ),
    "help.guide.premium.header": "⭐ <b>Ce que Premium vous offre</b>\n",
    "help.guide.premium.text": (
        "💬 Questions illimitées au coach\n"
        "🧠 Analyse IA approfondie de la progression\n"
        "🎁 Recommandations personnalisées avec le nom de votre animal\n\n"
    ),
    "help.guide.commands": "<b>Commandes :</b> /menu · /start · /reset",
    "help.support.btn": "💬 Contacter le support",
    "help.btn": "❓ Aide",
    "help.back_settings.btn": "🔙 Retour aux paramètres",
    # ── Edit Profile ───────────────────────────────────────────────────────────
    "edit_profile.title": "✏️ <b>Modifier le profil</b>\n\nQue souhaitez-vous modifier ?",
    "edit_profile.field.name.prompt": "Entrez le nouveau nom de l'animal dans le chat :",
    "edit_profile.field.breed.prompt": "Entrez la nouvelle race dans le chat :",
    "edit_profile.field.goal.prompt": "Écrivez le nouvel objectif d'entraînement dans le chat :",
    "edit_profile.field.level.prompt": "Choisissez le nouveau niveau d'obéissance :",
    "edit_profile.field.age.prompt": "Choisissez la nouvelle catégorie d'âge :",
    "edit_profile.field.size.prompt": "Choisissez la nouvelle taille de l'animal :",
    "edit_profile.field.timezone.prompt": "🌍 Choisissez votre fuseau horaire :",
    "edit_profile.saved": "✅ Mis à jour : <b>{value}</b>",
    "edit_profile.edit_more.btn": "✏️ Modifier encore",
    "edit_profile.error.empty": "⚠️ Le champ ne peut pas être vide. Réessayez.",
    "edit_profile.error.too_long": "⚠️ Valeur trop longue — 50 caractères max (le vôtre : {n}).",
    "edit_profile.btn.name": "🐾 Nom",
    "edit_profile.btn.breed": "🐕 Race",
    "edit_profile.btn.goal": "🎯 Objectif",
    "edit_profile.btn.level": "🎓 Niveau",
    "edit_profile.btn.age": "🎂 Âge",
    "edit_profile.btn.size": "📏 Taille",
    "edit_profile.btn.timezone": "🌍 Fuseau horaire",
    "edit_profile.cancel.btn": "🔙 Annuler",
    "edit_profile.level.1": "1 — Ne connaît aucune commande",
    "edit_profile.level.2": "2 — Connaît les bases (assis, debout)",
    "edit_profile.level.3": "3 — Obéit à la maison",
    "edit_profile.level.4": "4 — Obéit malgré les distractions",
    "edit_profile.level.5": "5 — Excellemment dressé",
    "edit_profile.size.small": "Petit (jusqu'à 10 kg)",
    "edit_profile.size.medium": "Moyen (10–25 kg)",
    "edit_profile.size.large": "Grand (25–45 kg)",
    "edit_profile.size.giant": "Géant (45+ kg)",
    "edit_profile.age.1": "Chiot (jusqu'à 4 mois)",
    "edit_profile.age.2": "Chiot (4–12 mois)",
    "edit_profile.age.3": "Jeune (1–3 ans)",
    "edit_profile.age.4": "Adulte (3–7 ans)",
    "edit_profile.age.5": "Senior (7+ ans)",
}
