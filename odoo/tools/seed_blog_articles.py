#!/usr/bin/env python3
"""Seed Pepito blog: rename, 5 articles, homepage block.

Run inside odoo_pepito_app:
  podman exec -i odoo_pepito_app python3 /path/or via stdin
  or: podman cp + exec
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta

sys.path.insert(0, "/usr/lib/python3/dist-packages")

import odoo  # noqa: E402
import odoo.api  # noqa: E402
import odoo.modules.registry  # noqa: E402
from odoo.tools import config  # noqa: E402

config.parse_config(
    [
        "--config",
        "/etc/odoo/odoo.conf",
        "--database",
        "odoo_user_pepito",
        "--no-http",
    ]
)

COVERS = [
    "/website_blog/static/src/img/cover_1.jpg",
    "/website_blog/static/src/img/cover_2.jpg",
    "/website_blog/static/src/img/cover_5.jpg",
    "/website_blog/static/src/img/blog_1.jpeg",
    "/website_blog/static/src/img/blog_2.jpeg",
]

BOT = "https://t.me/pepitopetbot"
SHOP = "https://pepitopet.ru/shop"
SHOP_TREATS = "https://pepitopet.ru/shop?categ=4&utm_source=blog&utm_medium=article"
SHOP_PUPPY = "https://pepitopet.ru/shop?tags=3&utm_source=blog&utm_medium=article"


def j(text: str) -> dict:
    """Translated field as en_US + ru_RU (site is RU-first)."""
    return {"en_US": text, "ru_RU": text}


def cover(url: str, opacity: str = "0.45") -> str:
    return json.dumps(
        {
            "background-image": f"url('{url}')",
            "resize_class": "o_record_has_cover o_half_screen_height",
            "opacity": opacity,
            "background_color_class": "o_cc o_cc5",
            "background_color_style": "",
        }
    )


def article_html(body_blocks: str) -> str:
    """Wrap article body with Pepito CTAs."""
    return f"""
<div class="container o_wblog_post_content_field">
{body_blocks}
<section class="mt-5 mb-4 p-4 rounded-3" style="background:#FBF3E8;border:1px solid rgba(26,10,0,0.08);">
  <h3 style="color:#1A0A00;font-family:'Playfair Display',serif;">Нужен персональный план?</h3>
  <p style="color:#5A3E28;margin-bottom:1rem;">AI‑кинолог Pepito в Telegram учтёт породу, возраст и цель — и подскажет шаги на сегодня.
  Бесплатно до 5 запросов в день.</p>
  <p class="mb-0">
    <a class="btn btn-primary me-2 mb-2" href="{BOT}" target="_blank" rel="noopener"
       style="background:#229ED9;border:none;">Открыть AI‑кинолога</a>
    <a class="btn btn-secondary mb-2" href="{SHOP_TREATS}">Сушёные лакомства</a>
  </p>
</section>
<p class="text-muted small"><em>Материал носит ознакомительный характер и не заменяет очную консультацию кинолога или ветеринара.
Pepito не ставит медицинских диагнозов.</em></p>
</div>
"""


ARTICLES = [
    {
        "name": "Собака тянет поводок: 3 шага, которые работают",
        "subtitle": "Спокойная прогулка без рывков — за 10–15 минут практики в день",
        "seo_name": "sobaka-tyanet-povodok",
        "meta_title": "Собака тянет поводок — что делать | Pepito",
        "meta_desc": "Практичные шаги: остановка при натяжении, смена направления, награда у ноги. Без рывков и крика. Советы AI‑кинолога Pepito.",
        "meta_kw": "собака тянет поводок, дрессировка, прогулка с собакой, кинолог",
        "tags": ["поведение", "прогулка"],
        "cover": COVERS[0],
        "teaser": "Рывок поводка — сигнал, что цель впереди важнее вас. Меняем правила игры: стоп, поворот, награда у ноги.",
        "content": article_html(
            f"""
<p class="lead">Если собака тащит вперёд, дело почти никогда не в «упрямстве». Чаще это привычка: натяжение = быстрее к цели.
Хорошая новость — привычку можно переписать за несколько коротких сессий.</p>

<h2>🎯 Главная причина</h2>
<p>Собака научилась: «тяну → идём туда, куда хочу». Пока это работает, она будет тянуть. Наша задача — сделать натяжение <strong>бесполезным</strong>,
а спокойный шаг рядом — <strong>выгодным</strong>.</p>

<h2>🛠 Что делать (3 шага)</h2>
<ol>
  <li><strong>Стоп при натяжении.</strong> Поводок натянулся — вы замираете. Идёте только когда поводок провис. Первые минуты будет «пила» — это нормально.</li>
  <li><strong>Смена направления.</strong> Тянет к столбу — разворачиваетесь и 5–10 шагов в другую сторону. Собака учится следить за вами, а не тащить к стимулу.</li>
  <li><strong>Награда у ноги.</strong> Мягкое лакомство (сушёное лёгкое, рубец мелкими кусочками) — только когда собака идёт рядом или смотрит на вас.
  Не из руки впереди морды на натянутом поводке.</li>
</ol>

<h2>🚫 Чего не делать</h2>
<ul>
  <li>Не дёргать поводок «в ответ» — это повышает возбуждение и портит доверие.</li>
  <li>Не ждать идеальной прогулки 40 минут: лучше 2×10 минут чистой практики.</li>
  <li>Не начинать учение у собачьей площадки в час пик — слишком много стимулов.</li>
</ul>

<blockquote class="blockquote my-4 p-3" style="border-left:4px solid #C45C26;background:#fff;">
  <p class="mb-0">Маленький кусочек сушёного лакомства работает лучше, чем большой кусок: можно чаще награждать, не перекормив.</p>
</blockquote>

<p><a href="{SHOP_TREATS}">Подобрать мягкие лакомства для прогулки →</a>
· <a href="{BOT}" target="_blank" rel="noopener">Разобрать вашу ситуацию с AI‑кинологом →</a></p>
"""
        ),
    },
    {
        "name": "Лакомства для щенка: как выбрать без вреда",
        "subtitle": "Размер, жёсткость и частота — чеклист для щенков 2–12 месяцев",
        "seo_name": "lakomstva-dlya-shchenka",
        "meta_title": "Лакомства для щенка — как выбрать | Pepito",
        "meta_desc": "Какие сушёные лакомства подходят щенку, какой размер кусочка безопасен и как не переборщить с наградой на дрессировке.",
        "meta_kw": "лакомства для щенка, сушёные лакомства, щенку можно, натуральные лакомства",
        "tags": ["щенок", "лакомства"],
        "cover": COVERS[1],
        "teaser": "Щенку важны мягкость, размер «в один укус» и отсутствие специй. Жёсткие кости и огромные трубки — на потом.",
        "content": article_html(
            f"""
<p class="lead">Щенок учится миру через рот. Лакомство — и награда, и риск, если размер или жёсткость не подходят возрасту.
Ниже — простой чеклист, которым мы пользуемся сами.</p>

<h2>Что важно в 2–12 месяцев</h2>
<ul>
  <li><strong>Мягкость.</strong> Лёгкое, печень, тонкие слайсы рубца — удобно рвать на крошки для дрессировки.</li>
  <li><strong>Размер.</strong> Кусочек должен съедаться за 1–2 секунды. Иначе щенок «зависает» и теряет фокус на упражнении.</li>
  <li><strong>Состав.</strong> Однокомпонентные сушёные субпродукты без соли, специй и сахара — база.</li>
  <li><strong>Нагрузка на ЖКТ.</strong> Новый продукт — с 1–2 кусочков. Следите за стулом 24 часа.</li>
</ul>

<h2>Что отложить</h2>
<ul>
  <li>Очень жёсткие долгоиграющие кости и толстые трубки — пока не окрепнут зубы и челюсть (ориентир: после смены зубов, индивидуально).</li>
  <li>Огромные куски, которые щенок может попытаться проглотить целиком.</li>
  <li>«Человеческие» снеки: колбаса, сыр с солью, сладкое.</li>
</ul>

<h2>Как встроить в тренировку</h2>
<ol>
  <li>10–15 крошек на сессию «сидеть / ко мне / рядом».</li>
  <li>После занятия — спокойное жевание <em>подходящего</em> кусочка на коврике (сброс возбуждения).</li>
  <li>Суточная доля лакомств — разумная часть рациона; основной корм не вытесняем «наградами».</li>
</ol>

<p><a href="{SHOP_PUPPY}">Смотреть подборку для щенков →</a>
· <a href="{SHOP_TREATS}">Все сушёные лакомства →</a>
· <a href="{BOT}" target="_blank" rel="noopener">Спросить AI‑кинолога про вашего щенка →</a></p>
"""
        ),
    },
    {
        "name": "Собака лает на гостей: план на 7 дней",
        "subtitle": "От «охранника у двери» к спокойному приветствию — без крика и наказаний",
        "seo_name": "sobaka-laet-na-gostey",
        "meta_title": "Собака лает на гостей — план на неделю | Pepito",
        "meta_desc": "Пошаговый план: коврик, сигнал двери, награда за тишину, помощь гостя. Как снизить лай без жёстких методов.",
        "meta_kw": "собака лает на гостей, лай собаки, дрессировка, поведение",
        "tags": ["поведение", "дом"],
        "cover": COVERS[2],
        "teaser": "Лай на звонок — часто смесь возбуждения и охраны. Учим альтернативу: место → тишина → награда.",
        "content": article_html(
            f"""
<p class="lead">Лай на гостей редко лечится фразой «фу». Нужна понятная собаке альтернатива и предсказуемый сценарий у двери.
Ниже — мягкий план на неделю.</p>

<h2>🎯 Что происходит</h2>
<p>Звонок/стук → всплеск возбуждения → лай «сработал». Если гость всё равно входит, а вы суетитесь, лай закрепляется как часть ритуала.</p>

<h2>🛠 План на 7 дней</h2>
<ol>
  <li><strong>День 1–2. Коврик = место.</strong> Учите «место» в тишине: коврик → награда. Без двери.</li>
  <li><strong>День 3. Звук без гостя.</strong> Запись звонка на низкой громкости. Звук → «место» → награда <em>за тишину</em> на коврике.</li>
  <li><strong>День 4–5. Репетиция с помощником.</strong> Друг звонит, ждёт. Вы спокойно ведёте собаку на место. Открываете дверь, только когда есть пауза в лае.</li>
  <li><strong>День 6–7. Короткие реальные визиты.</strong> Гость игнорирует собаку 30–60 секунд. Награда — за контакт с вами/ковриком, не за прыжки на гостя.</li>
</ol>

<h2>🚫 Частые ошибки</h2>
<ul>
  <li>Кричать поверх лая — для собаки это «подпевание».</li>
  <li>Пускать гостя сразу «чтобы успокоилась» — подкрепляет сценарий.</li>
  <li>Наказывать после лая — страх у двери часто усиливает вокализацию.</li>
</ul>

<p>Если лай сочетается с сильной тревогой или агрессией — лучше очный кинолог. AI‑кинолог Pepito поможет разобрать бытовой сценарий и дать шаги под вашу собаку.</p>

<p><a href="{BOT}" target="_blank" rel="noopener">Разобрать лай с AI‑кинологом →</a>
· <a href="{SHOP_TREATS}">Лакомства для тренировки «места» →</a></p>
"""
        ),
    },
    {
        "name": "Долгоиграющие лакомства: когда они спасают нервы",
        "subtitle": "Жевание как инструмент: смена режима, «один дома», после прогулки",
        "seo_name": "dolgoigrayushchie-lakomstva",
        "meta_title": "Долгоиграющие лакомства для собак | Pepito",
        "meta_desc": "Когда давать рубец, трахею, бычий корень: после возбуждения, на смене режима, когда собака остаётся одна. Правила безопасности.",
        "meta_kw": "долгоиграющие лакомства, жевательные лакомства, рубец, трахея, собака одна дома",
        "tags": ["лакомства", "дом"],
        "cover": COVERS[3],
        "teaser": "Жевание снижает возбуждение. Правильный «долгоиграющий» кусок — не скука, а гигиена нервной системы.",
        "content": article_html(
            f"""
<p class="lead">После активной прогулки или когда вы уходите, собаке нужен легальный способ «дожевать день».
Сушёные долгоиграющие лакомства — один из самых простых инструментов, если соблюдать размер и контроль.</p>

<h2>Когда особенно полезны</h2>
<ul>
  <li><strong>После тренировки или гостей</strong> — переход из возбуждения в покой.</li>
  <li><strong>Смена режима</strong> (вы на созвоне, ребёнок делает уроки) — занятие пастью вместо носа в ваши дела.</li>
  <li><strong>Короткие «один дома»</strong> — при условии, что собака уже умеет оставаться спокойно и лакомство безопасно по размеру.</li>
</ul>

<h2>Как выбирать</h2>
<ol>
  <li>Кусок <strong>больше морды</strong>, но такой, чтобы нельзя было проглотить целиком.</li>
  <li>Для мощных жевателей — более плотные варианты; для мягких челюстей — рубец, вымя, тонкая трахея.</li>
  <li>Всегда свежая вода рядом. Убирайте, когда остался острый/маленький фрагмент.</li>
</ol>

<h2>Правила безопасности</h2>
<ul>
  <li>Первый раз — под присмотром 10–15 минут.</li>
  <li>Не оставляйте незнакомый жёсткий продукт щенку без присмотра.</li>
  <li>При склонности к заглатыванию крупных кусков — только мягкие рвущиеся слайсы.</li>
</ul>

<blockquote class="blockquote my-4 p-3" style="border-left:4px solid #C45C26;background:#fff;">
  <p class="mb-0">Долгоиграющее лакомство не заменяет прогулку и общение. Это дополнение к режиму, а не «выключатель» собаки на весь день.</p>
</blockquote>

<p><a href="{SHOP_TREATS}">Каталог сушёных лакомств →</a>
· <a href="{BOT}" target="_blank" rel="noopener">Подобрать тип жевания под характер →</a></p>
"""
        ),
    },
    {
        "name": "AI‑кинолог Pepito: как пользоваться ботом с умом",
        "subtitle": "Онбординг, лимиты free/premium, планы тренировок и голос — короткий гид",
        "seo_name": "ai-kinolog-pepito-kak-polzovatsya",
        "meta_title": "AI‑кинолог Pepito в Telegram — как пользоваться",
        "meta_desc": "Как начать диалог с AI‑кинологом, зачем указывать породу и цель, чем premium отличается от free, и как отмечать задания плана.",
        "meta_kw": "AI кинолог, telegram бот для собак, pepito, дрессировка онлайн",
        "tags": ["ai-кинолог", "гайд"],
        "cover": COVERS[4],
        "teaser": "Бот силён, когда знает питомца. 2 минуты онбординга экономят 20 минут бессмысленных общих советов.",
        "content": article_html(
            f"""
<p class="lead"><a href="{BOT}" target="_blank" rel="noopener">@pepitopetbot</a> — AI‑кинолог в Telegram: отвечает на вопросы по поведению,
собирает план на день/неделю и помогает отмечать прогресс. Ниже — как выжать максимум с первой сессии.</p>

<h2>1. Онбординг: не пропускайте</h2>
<p>Укажите <strong>кличку, породу/размер, возраст, цель</strong> (например: «не тянуть поводок»).
От этого зависят и советы, и рекомендации лакомств в магазине.</p>

<h2>2. Free и Premium</h2>
<ul>
  <li><strong>Free</strong> — до 5 AI‑запросов в день: хватает, чтобы попробовать формат и решить одну задачу.</li>
  <li><strong>Premium</strong> (Telegram Stars) — выше лимиты, длиннее контекст диалога, удобнее вести программу.</li>
</ul>

<h2>3. Как спрашивать, чтобы ответ был полезным</h2>
<ol>
  <li>Опишите <em>контекст</em>: где, когда, что уже пробовали.</li>
  <li>Одна проблема = один запрос. «Тянет + лает + грызёт» лучше разбить.</li>
  <li>После совета — короткий фидбек: «сделали, стало лучше/хуже» — бот точнее ведёт дальше.</li>
</ol>

<h2>4. Планы и «выполнили упражнение»</h2>
<p>Бот может собрать план на день. Когда сделали задачу — напишите голосом или текстом «сделали остановку при натяжении».
Система отметит задание, если поймёт намёк; при нескольких задачах лучше назвать упражнение явно.</p>

<h2>5. Чего бот не делает</h2>
<ul>
  <li>Не ставит ветеринарные диагнозы и не назначает лекарства.</li>
  <li>Не заменяет очную работу при агрессии к людям/собакам.</li>
</ul>

<p><a class="btn btn-primary" href="{BOT}" target="_blank" rel="noopener" style="background:#229ED9;border:none;">Открыть @pepitopetbot</a>
&nbsp; <a href="{SHOP}">В магазин Pepito →</a></p>
"""
        ),
    },
]


HOMEPAGE_SECTION = """
<section class="s_pepito_blog pt64 pb64 o_colored_level" data-snippet="s_text_block" data-name="Советы кинолога" style="background:#FBF3E8;">
  <div class="container">
    <div class="row mb-4 align-items-end">
      <div class="col-lg-8">
        <p class="text-uppercase small fw-semibold mb-2" style="color:#C45C26;letter-spacing:0.08em;">Журнал Pepito</p>
        <h2 class="mb-2" style="color:#1A0A00;font-family:'Playfair Display',serif;font-weight:700;">Советы кинолога</h2>
        <p class="mb-0" style="color:#5A3E28;max-width:36rem;">Поведение, щенки, лакомства и AI‑кинолог — коротко и по делу. Без воды и без «ветеринарных диагнозов».</p>
      </div>
      <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
        <a href="/blog" class="btn btn-secondary">Все статьи</a>
      </div>
    </div>
    <div class="row g-4">
      {cards}
    </div>
  </div>
</section>
"""


def card_html(title: str, teaser: str, url: str, tag: str) -> str:
    return f"""
      <div class="col-md-6 col-lg-4">
        <a href="{url}" class="text-decoration-none d-block h-100" style="color:inherit;">
          <div class="h-100 border-0" style="border-radius:20px;background:#fff;box-shadow:0 8px 32px rgba(26,10,0,0.08);padding:28px 24px;transition:transform .15s ease;">
            <span class="d-inline-block mb-3 small fw-semibold" style="color:#C45C26;background:rgba(196,92,38,0.10);padding:4px 10px;border-radius:999px;">{tag}</span>
            <h3 class="h5 mb-2" style="color:#1A0A00;font-family:'Playfair Display',serif;font-weight:700;line-height:1.35;">{title}</h3>
            <p class="mb-3 small" style="color:#5A3E28;line-height:1.55;">{teaser}</p>
            <span class="fw-semibold" style="color:#C45C26;">Читать →</span>
          </div>
        </a>
      </div>
"""


def main() -> int:
    registry = odoo.modules.registry.Registry.new("odoo_user_pepito")
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        website = env["website"].search([("id", "=", 1)], limit=1) or env["website"].search([], limit=1)
        blog = env["blog.blog"].search([], limit=1, order="id")
        if not blog:
            blog = env["blog.blog"].create(
                {
                    "name": "Советы кинолога",
                    "subtitle": "Поведение, лакомства и AI‑кинолог Pepito",
                    "website_id": website.id,
                }
            )
            print(f"created blog id={blog.id}")
        else:
            blog.write(
                {
                    "name": j("Советы кинолога"),
                    "subtitle": j("Поведение, лакомства и AI‑кинолог Pepito"),
                    "website_meta_title": j("Советы кинолога | Pepito Pet"),
                    "website_meta_description": j(
                        "Практичные статьи о дрессировке, щенках и натуральных лакомствах. Блог Pepito и AI‑кинолог в Telegram."
                    ),
                    "seo_name": j("sovety-kinologa"),
                    "cover_properties": cover(COVERS[0], "0.5"),
                    "active": True,
                    "website_id": website.id,
                }
            )
            print(f"renamed blog id={blog.id}")

        # tags (match by resolved display name)
        tag_map = {}
        tag_defs = [
            ("поведение", 1),
            ("прогулка", 2),
            ("щенок", 3),
            ("лакомства", 4),
            ("дом", 5),
            ("ai-кинолог", 6),
            ("гайд", 7),
        ]
        Tag = env["blog.tag"]

        def _tag_label(rec) -> str:
            n = rec.with_context(lang="ru_RU").name
            if isinstance(n, dict):
                return str(n.get("ru_RU") or n.get("en_US") or "")
            return str(n or "")

        for tname, color in tag_defs:
            found = next((t for t in Tag.search([]) if _tag_label(t).lower() == tname.lower()), None)
            if found:
                tag_map[tname] = found
            else:
                tag_map[tname] = Tag.create({"name": tname, "color": color})
            print(f"  tag {tname} -> {tag_map[tname].id}")

        # remove old empty demo state: unpublish nothing; create/update by seo_name
        Post = env["blog.post"]
        author = env.ref("base.partner_admin")
        created_posts = []
        now = datetime.utcnow()

        for i, art in enumerate(ARTICLES):
            post_date = now - timedelta(hours=i * 5)
            tag_ids = [tag_map[t].id for t in art["tags"] if t in tag_map]

            domain = [("blog_id", "=", blog.id)]
            candidates = Post.search(domain)
            post = Post.browse()
            for p in candidates:
                sn = p.seo_name
                if isinstance(sn, dict):
                    sn = sn.get("ru_RU") or sn.get("en_US") or ""
                name = p.name
                if isinstance(name, dict):
                    name = name.get("ru_RU") or name.get("en_US") or ""
                if sn == art["seo_name"] or name == art["name"]:
                    post = p
                    break

            vals = {
                "name": j(art["name"]),
                "subtitle": j(art["subtitle"]),
                "blog_id": blog.id,
                "website_id": website.id,
                "author_id": author.id,
                "author_name": "Pepito · AI‑кинолог",
                "content": j(art["content"]),
                "teaser_manual": j(art["teaser"]),
                "cover_properties": cover(art["cover"]),
                "is_published": True,
                "active": True,
                "published_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                "post_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                "website_meta_title": j(art["meta_title"]),
                "website_meta_description": j(art["meta_desc"]),
                "website_meta_keywords": j(art["meta_kw"]),
                "seo_name": j(art["seo_name"]),
                "is_seo_optimized": True,
                "header_visible": True,
                "footer_visible": True,
                "tag_ids": [(6, 0, tag_ids)],
            }
            if post:
                post.write(vals)
                print(f"updated post id={post.id} {art['name'][:40]}")
            else:
                post = Post.create(vals)
                print(f"created post id={post.id} {art['name'][:40]}")
            created_posts.append((post, art))

        # Commit posts first so content survives even if homepage tweak fails
        cr.commit()
        print("posts committed")

        # Homepage block — static cards with real URLs (XML-safe)
        import re

        cards = []
        for post, art in created_posts[:5]:
            url = (post.website_url or f"/blog/{post.id}").replace("&", "&amp;")
            tag = art["tags"][0] if art["tags"] else "советы"
            title = art["name"].replace("&", "&amp;")
            teaser = art["teaser"].replace("&", "&amp;")
            cards.append(card_html(title, teaser, url, tag))
        section = HOMEPAGE_SECTION.format(cards="".join(cards))
        # collapse newlines in section to keep arch compact
        section = re.sub(r"\n\s*", "\n", section).strip() + "\n"

        # Update arch_db via SQL (avoids some view combine edge-cases on write)
        cr.execute("SELECT arch_db FROM ir_ui_view WHERE id = 554")
        row = cr.fetchone()
        if not row:
            print("WARN: homepage view 554 not found — skip homepage block")
        else:
            arch_db = row[0]
            if isinstance(arch_db, str):
                arch_db = json.loads(arch_db)
            new_arch = {}
            for lang, html in arch_db.items():
                if not html or not isinstance(html, str):
                    new_arch[lang] = html
                    continue
                h = html
                if "s_pepito_blog" in h:
                    h = re.sub(
                        r'<section class="s_pepito_blog[\s\S]*?</section>\s*',
                        "",
                        h,
                        count=1,
                    )
                marker = '<section class="s_cta_box'
                if marker in h:
                    h = h.replace(marker, section + marker, 1)
                elif "s_pepito_blog" not in h:
                    # fallback: before last structure close
                    h = h.replace(
                        "</div>\n    </t>\n</t>",
                        section + "</div>\n    </t>\n</t>",
                        1,
                    )
                new_arch[lang] = h
            cr.execute(
                "UPDATE ir_ui_view SET arch_db = %s::jsonb, write_date = (now() at time zone 'UTC') WHERE id = 554",
                [json.dumps(new_arch, ensure_ascii=False)],
            )
            print("homepage view id=554 updated with blog section (SQL)")

        cr.commit()

        # Clear caches
        try:
            env.registry.clear_cache()
        except Exception as e:
            print("cache clear:", e)

        print("DONE")
        for post, art in created_posts:
            print(f"  {post.website_url}  ::  {art['name'][:50]}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
