#!/usr/bin/env python3
"""Publish 5 more Pepito blog posts (batch 2) + refresh homepage cards."""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timedelta

sys.path.insert(0, "/usr/lib/python3/dist-packages")

import odoo  # noqa: E402
import odoo.api  # noqa: E402
import odoo.modules.registry  # noqa: E402
from odoo.tools import config  # noqa: E402

config.parse_config(
    ["--config", "/etc/odoo/odoo.conf", "--database", "odoo_user_pepito", "--no-http"]
)

BOT = "https://t.me/pepitopetbot"
SHOP_TREATS = "https://pepitopet.ru/shop?categ=4&utm_source=blog&utm_medium=article"
SHOP_PUPPY = "https://pepitopet.ru/shop?tags=3&utm_source=blog&utm_medium=article"
SHOP = "https://pepitopet.ru/shop?utm_source=blog&utm_medium=article"
COVER_PLACEHOLDER = "/website_blog/static/src/img/cover_2.jpg"


def set_trans(record, field: str, value: str) -> None:
    for lang in ("ru_RU", "en_US"):
        record.with_context(lang=lang).write({field: value})


def cover(url: str, opacity: str = "0.4") -> str:
    return json.dumps(
        {
            "background-image": f"url('{url}')",
            "resize_class": "o_record_has_cover o_half_screen_height",
            "opacity": opacity,
            "background_color_class": "o_cc o_cc5",
            "background_color_style": "",
        }
    )


def article_html(body: str) -> str:
    return f"""
<div class="container o_wblog_post_content_field">
{body}
<section class="mt-5 mb-4 p-4 rounded-3" style="background:#FBF3E8;border:1px solid rgba(26,10,0,0.08);">
  <h3 style="color:#1A0A00;font-family:'Playfair Display',serif;">Нужен персональный план?</h3>
  <p style="color:#5A3E28;margin-bottom:1rem;">AI‑кинолог Pepito в Telegram учтёт породу, возраст и цель.
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
        "name": "Собака грызёт мебель и плинтуса: план до «ремонта»",
        "subtitle": "Скука, тревога или смена зубов — разводим причины и даём легальную альтернативу",
        "seo_name": "sobaka-gryzyot-mebel",
        "meta_title": "Собака грызёт мебель — что делать | Pepito",
        "meta_desc": "Почему собака грызёт плинтуса и диван, чем отличается щенковый зуд от скуки, и как ввести легальное жевание без крика.",
        "meta_kw": "собака грызёт мебель, грызёт плинтус, щенок грызёт, долгоиграющие лакомства",
        "tags": ["поведение", "дом"],
        "teaser": "Мебель — не «месть». Чаще это зубы, скука или тревога. Сначала легальный chew и режим, потом ограничения.",
        "content": article_html(
            f"""
<p class="lead">Облизанный угол дивана и погрызенный плинтус бесят. Но пока вы только ругаете «после факта»,
собака не учится <em>что</em> можно — она учится «когда хозяина нет, правила другие».</p>

<h2>🎯 Три разные причины</h2>
<ul>
  <li><strong>Смена зубов / зуд</strong> (чаще щенки и молодые) — нужно что-то жевать.</li>
  <li><strong>Скука и недогул</strong> — мало движения и задач для носа/пасти.</li>
  <li><strong>Тревога «один дома»</strong> — жевание как способ сбросить стресс (иногда вместе с воем).</li>
</ul>
<p>План ниже — для бытовых случаев. При разрушениях только в ваше отсутствие + сильная паника — лучше очный кинолог.</p>

<h2>🛠 Что делать (по шагам)</h2>
<ol>
  <li><strong>Легальный chew до ухода.</strong> Долгоиграющее сушёное лакомство подходящего размера — на коврике, не на диване.
  <a href="{SHOP_TREATS}">Каталог жевательных лакомств →</a></li>
  <li><strong>Зона доступа.</strong> Пока учитесь — не весь дом. Одна комната / вольер / дверь, где нет «дорогих» предметов.</li>
  <li><strong>Режим до разлуки.</strong> 15–20 минут спокойной прогулки или нюхательной игры → туалет → chew → уход без долгих прощаний.</li>
  <li><strong>Обогащение.</strong> Прячьте 5–10 мелких кусочков по коврику (поиск носом), а не только «миска и всё».</li>
  <li><strong>Ловите хорошее.</strong> Нашли собаку на коврике с разрешённым chew — тихо похвалили. Не ор за уже погрызенный плинтус час назад.</li>
</ol>

<h2>🚫 Чего не делать</h2>
<ul>
  <li>Бить, тыкать мордой в ущерб, орать после возвращения — связь «вы пришли = страшно».</li>
  <li>Оставлять щенка с огромной жёсткой костью без присмотра.</li>
  <li>Заменять прогулку только chew — жевание дополняет режим, не отменяет его.</li>
</ul>

<blockquote class="blockquote my-4 p-3" style="border-left:4px solid #C45C26;background:#fff;">
  <p class="mb-0">Связка с <a href="/blog">статьёй про долгоиграющие лакомства</a>: жевание — инструмент спокойствия, если размер и контроль в порядке.</p>
</blockquote>

<p><a href="{BOT}" target="_blank" rel="noopener">Разобрать ваш сценарий с AI‑кинологом →</a>
· <a href="{SHOP_TREATS}">Подобрать chew →</a></p>
"""
        ),
    },
    {
        "name": "Первая прогулка щенка: чеклист на 14 дней",
        "subtitle": "Короткие выходы, безопасные места и награды — без марафона в первый день",
        "seo_name": "pervaya-progulka-shchenka",
        "meta_title": "Первая прогулка щенка — чеклист 14 дней | Pepito",
        "meta_desc": "Как выводить щенка гулять после прививок: длительность, места, лакомства-награды, что делать если пугается. Чеклист на две недели.",
        "meta_kw": "первая прогулка щенка, щенок гулять, социализация щенка, лакомства на прогулке",
        "tags": ["щенок", "прогулка"],
        "teaser": "Не 40 минут с первого дня. 5–10 минут, тихий двор, крошки-награды — и щенок учится, что улица = с вами безопасно.",
        "content": article_html(
            f"""
<p class="lead">Первые прогулки закладывают отношение к миру: «улица страшная» или «улица интересная рядом с человеком».
Ниже — практичный чеклист на 14 дней (сроки прививок и разрешение гулять — по вашей схеме вакцинации и совету ветклиники).</p>

<h2>До выхода из подъезда</h2>
<ul>
  <li>Шлейка/ошейник по размеру, короткий поводок, пакеты.</li>
  <li>Мелкие <strong>мягкие</strong> лакомства «в один укус» —
  <a href="{SHOP_PUPPY}">подборка для щенков →</a>.</li>
  <li>Цель выхода: не «вымотать», а <strong>положительный опыт</strong>.</li>
</ul>

<h2>🛠 Дни 1–5: знакомство</h2>
<ol>
  <li>5–10 минут у дома / тихий двор. Много нюхания — это норма и даже польза.</li>
  <li>Каждый спокойный шаг рядом с вами — крошка. Не кормите с натянутого поводка «вперёд».</li>
  <li>Увидел пугалку (шум, человек) — увеличили дистанцию, наградили за взгляд на вас.</li>
</ol>

<h2>🛠 Дни 6–14: чуть дальше</h2>
<ol>
  <li>+2–5 минут и один новый «спокойный» маршрут.</li>
  <li>Короткая практика «поводок провис → идём» (см. статью про поводок).</li>
  <li>После улицы — вода, отдых, иногда мягкий chew дома.</li>
</ol>

<h2>🚫 Частые ошибки</h2>
<ul>
  <li>Собачья площадка в час пик в первую неделю — перегруз стимулами.</li>
  <li>Тащить щенка за ошейник к объекту страха «чтобы привык».</li>
  <li>Огромные куски лакомств: щенок «зависает» и теряет фокус.</li>
</ul>

<p><a href="{BOT}" target="_blank" rel="noopener">Составить план прогулок под вашего щенка →</a>
· <a href="{SHOP_PUPPY}">Лакомства для щенка →</a>
· <a href="{SHOP_TREATS}">Все сушёные →</a></p>
"""
        ),
    },
    {
        "name": "Как не перекормить лакомствами на дрессировке",
        "subtitle": "Крошки vs жевание: таблица «когда что» и доля в рационе",
        "seo_name": "lakomstva-na-dressirovke-ne-perekormit",
        "meta_title": "Лакомства на дрессировке — как не перекормить | Pepito",
        "meta_desc": "Сколько лакомств можно на тренировке, чем отличается награда от долгоиграющего жевания, как считать долю рациона и не испортить аппетит.",
        "meta_kw": "лакомства на дрессировке, сколько лакомств собаке, перекормить собаку, награда за команду",
        "tags": ["лакомства", "гайд"],
        "teaser": "Награда — крошка на секунду. Жевание — отдельный инструмент. Путаете их — и вес, и фокус на тренировке страдают.",
        "content": article_html(
            f"""
<p class="lead">Сушёные лакомства — сильный инструмент обучения. Но если «награждать» огромными кусками или подменять ими ужин,
щенок или взрослая собака либо толстеет, либо перестаёт есть основной корм.</p>

<h2>Два разных продукта</h2>
<table class="table table-sm" style="max-width:36rem;">
  <thead><tr><th>Тип</th><th>Зачем</th><th>Размер</th></tr></thead>
  <tbody>
    <tr><td><strong>Тренировочная крошка</strong></td><td>Маркер «правильно»</td><td>1 укус, 1–2 сек</td></tr>
    <tr><td><strong>Долгоиграющий chew</strong></td><td>Сброс возбуждения, «один дома»</td><td>Дольше, под контролем</td></tr>
  </tbody>
</table>
<p><a href="{SHOP_TREATS}">Каталог →</a> — берите мягкое/тонкое на сессию и отдельный chew на покой.</p>

<h2>🛠 Практичные правила</h2>
<ol>
  <li><strong>Доля.</strong> Ориентир: лакомства в сумме не вытесняют основной рацион. Уменьшите ужин, если сессия была «сытной».</li>
  <li><strong>Режьте.</strong> Слайс лёгкого или печени — на 10–20 крошек. Так хватает на всю сессию без перекорма.</li>
  <li><strong>Ценность по сложности.</strong> Дома «сидеть» — обычная крошка; на улице у белок — чуть вкуснее кусочек.</li>
  <li><strong>Вода.</strong> После сушёного — доступ к воде.</li>
  <li><strong>Новый продукт.</strong> 1–2 кусочка в первый день, смотрите стул.</li>
</ol>

<h2>🚫 Типичные ошибки</h2>
<ul>
  <li>Кормить с руки огромным куском «за попытку» — собака жуёт 30 секунд и забыла задачу.</li>
  <li>Давать chew <em>во время</em> активной дрессировки «рядом» — это другая задача для мозга.</li>
  <li>Соль, специи, «человеческие» снеки как награда.</li>
</ul>

<blockquote class="blockquote my-4 p-3" style="border-left:4px solid #C45C26;background:#fff;">
  <p class="mb-0">AI‑кинолог подскажет структуру сессии; вы выбираете награду под этап. Напишите в боте: возраст, вес, сколько уже даёте лакомств.</p>
</blockquote>

<p><a href="{BOT}" target="_blank" rel="noopener">Спросить про рацион наград →</a>
· <a href="{SHOP}">В магазин Pepito →</a></p>
"""
        ),
    },
    {
        "name": "Собака не подходит по команде «ко мне» на улице",
        "subtitle": "Recall без крика: комната → двор → слабые стимулы → улица",
        "seo_name": "komanda-ko-mne-na-ulitse",
        "meta_title": "Команда «ко мне» на улице — как научить | Pepito",
        "meta_desc": "Как поставить надёжный подход к хозяину: пошаговая цепочка, страховка на поводке, high-value лакомства, ошибки которые ломают recall.",
        "meta_kw": "команда ко мне, recall собака, собака не подходит, дрессировка на улице",
        "tags": ["поведение", "прогулка"],
        "teaser": "На улице «ко мне» ломается, если учили только на кухне. Строим ценность подхода и не наказываем за опоздание.",
        "content": article_html(
            f"""
<p class="lead">Дома подбегает за крошку — на улице «глухая». Это не вредность: стимулы сильнее, а команда не дотягивает по ценности.
Recall (подзыв) строят цепочкой, а не ором через двор.</p>

<h2>🎯 Принцип</h2>
<p>Подойти к вам должно быть <strong>выгоднее</strong>, чем продолжать нюхать/играть. После подхода — джекпот (несколько high-value крошек), игра или продолжение прогулки,
а не сразу ошейник «и домой, ты виноват».</p>

<h2>🛠 Цепочка на 1–2 недели</h2>
<ol>
  <li><strong>Комната.</strong> Слово «ко мне» → шаг к вам → фейерверк крошек (печень, лёгкое — мелко).
  <a href="{SHOP_TREATS}">Выбрать «вкусняшки» →</a></li>
  <li><strong>Коридор / двор на длинном поводке.</strong> Отпустили 3–5 м, позвали один раз спокойно. Подошла — джекпот. Не подошла — мягко подтянули поводком <em>без скандала</em>, всё равно наградили за финиш у ног (сначала).</li>
  <li><strong>Слабый стимул.</strong> Другой человек вдалеке, запах травы — повтор.</li>
  <li><strong>Улица.</strong> Только на страховке (длинный поводок), пока % подхода не стабильный. Свободно — когда 9 из 10 без подсказки.</li>
</ol>

<h2>🚫 Ломает recall</h2>
<ul>
  <li>Звать 10 раз подряд — слово обесценивается.</li>
  <li>Подошла → сразу неприятная процедура (уколы, ругань, резкий конец гуляния каждый раз).</li>
  <li>Гоняться и хватать — игра «не догони».</li>
</ul>

<p>Параллельно можно подтянуть прогулку без рывков — см. статью про поводок. Оба навыка дружат.</p>

<p><a href="{BOT}" target="_blank" rel="noopener">Разобрать recall с AI‑кинологом →</a>
· <a href="{SHOP_TREATS}">High-value лакомства →</a></p>
"""
        ),
    },
    {
        "name": "Неделя с AI‑кинологом: что спросить в первые 7 дней",
        "subtitle": "Готовый roadmap диалогов — от онбординга до недельного плана",
        "seo_name": "nedelya-s-ai-kinologom",
        "meta_title": "Неделя с AI‑кинологом Pepito — план вопросов",
        "meta_desc": "Что писать боту @pepitopetbot каждый день первой недели: онбординг, одна проблема, план, фидбек, прогресс. Free и Premium.",
        "meta_kw": "AI кинолог, pepito бот, телеграм кинолог, план дрессировки",
        "tags": ["ai-кинолог", "гайд"],
        "teaser": "Не «научи всему». Один фокус в день + короткий фидбек — и бот становится полезным, а не общим чатом.",
        "content": article_html(
            f"""
<p class="lead"><a href="{BOT}" target="_blank" rel="noopener">@pepitopetbot</a> силён на коротких итерациях. Ниже — недельный сценарий,
чтобы не сжечь free-лимит впустую и увидеть прогресс.</p>

<h2>День 1 — Онбординг</h2>
<p>Кличка, порода/размер, возраст, <strong>одна</strong> главная цель (например: «не тянуть» или «спокойнее с гостями»).
Без этого советы будут общими.</p>

<h2>День 2 — Одна проблема, максимум контекста</h2>
<p>Где / когда / что уже пробовали / что делает собака. Пример: «Тянет только к другим собакам, на пустой улице норм».</p>

<h2>День 3 — План на сегодня</h2>
<p>Попросите дневной план (2 упражнения). Сделайте 10–15 минут. Отметьте текстом или голосом «сделали …».</p>

<h2>День 4–5 — Фидбек-петля</h2>
<ul>
  <li>«Сделали остановку при натяжении — стало чуть лучше»</li>
  <li>«На площадке срывается» → бот сузит задачу</li>
</ul>

<h2>День 6 — Недельный каркас</h2>
<p>Запросите week plan, если цель на курс. Не делайте все 7 дней идеально — важнее 4–5 коротких сессий.</p>

<h2>День 7 — Прогресс</h2>
<p>Попросите краткое резюме: что закрепить, что упростить. При необходимости — Premium Stars (длиннее контекст, комфортнее программа).</p>

<h2>Free vs Premium (коротко)</h2>
<ul>
  <li><strong>Free</strong> — до 5 AI-запросов/день: хватает на сценарий выше, если не спамить.</li>
  <li><strong>Premium</strong> — когда ведёте программу и несколько питомцев/целей.</li>
</ul>

<p>Полезные статьи журнала под цели:
<a href="/blog">поводок</a>, гости, щенок, chew, лакомства на дрессировке.</p>

<p><a class="btn btn-primary" href="{BOT}" target="_blank" rel="noopener" style="background:#229ED9;border:none;">Начать день 1 в боте</a>
&nbsp; <a href="{SHOP}">Магазин Pepito →</a></p>
"""
        ),
    },
]


def card_html(title: str, teaser: str, url: str, tag: str, img: str | None = None) -> str:
    img_block = ""
    if img:
        img_block = f"""<div style="height:180px;background:url('{img}') center/cover no-repeat;background-color:#FBF3E8;"></div>"""
    return f"""
      <div class="col-md-6 col-lg-4">
        <a href="{url}" class="text-decoration-none d-block h-100" style="color:inherit;">
          <div class="h-100 border-0 overflow-hidden" style="border-radius:20px;background:#fff;box-shadow:0 8px 32px rgba(26,10,0,0.08);transition:transform .15s ease;">
            {img_block}
            <div style="padding:22px 22px 24px;">
              <span class="d-inline-block mb-2 small fw-semibold" style="color:#C45C26;background:rgba(196,92,38,0.10);padding:4px 10px;border-radius:999px;">{tag}</span>
              <h3 class="h5 mb-2" style="color:#1A0A00;font-family:'Playfair Display',serif;font-weight:700;line-height:1.35;">{title}</h3>
              <p class="mb-3 small" style="color:#5A3E28;line-height:1.55;">{teaser}</p>
              <span class="fw-semibold" style="color:#C45C26;">Читать →</span>
            </div>
          </div>
        </a>
      </div>"""


def main() -> int:
    registry = odoo.modules.registry.Registry.new("odoo_user_pepito")
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        website = env["website"].browse(1)
        blog = env["blog.blog"].search([], limit=1, order="id")
        author = env.ref("base.partner_admin")
        Tag = env["blog.tag"]
        Post = env["blog.post"]

        def tag_label(t) -> str:
            n = t.with_context(lang="ru_RU").name
            return str(n or "")

        tag_map = {}
        for tname, color in [
            ("поведение", 1),
            ("прогулка", 2),
            ("щенок", 3),
            ("лакомства", 4),
            ("дом", 5),
            ("ai-кинолог", 6),
            ("гайд", 7),
            ("тренировка", 8),
        ]:
            found = next((t for t in Tag.search([]) if tag_label(t).lower() == tname.lower()), None)
            tag_map[tname] = found or Tag.create({"name": tname, "color": color})

        now = datetime.utcnow()
        created = []
        for i, art in enumerate(ARTICLES):
            # find existing by seo
            post = None
            for p in Post.search([("blog_id", "=", blog.id)]):
                sn = p.with_context(lang="ru_RU").seo_name or ""
                if sn == art["seo_name"] or art["seo_name"] in str(p.seo_name):
                    post = p
                    break
            tag_ids = [tag_map[t].id for t in art["tags"] if t in tag_map]
            post_date = now - timedelta(hours=i * 3)
            vals_common = {
                "blog_id": blog.id,
                "website_id": website.id,
                "author_id": author.id,
                "author_name": "Pepito · AI‑кинолог",
                "is_published": True,
                "active": True,
                "is_seo_optimized": True,
                "header_visible": True,
                "footer_visible": True,
                "published_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                "post_date": post_date.strftime("%Y-%m-%d %H:%M:%S"),
                "cover_properties": cover(COVER_PLACEHOLDER),
                "tag_ids": [(6, 0, tag_ids)],
            }
            if not post:
                post = Post.create({**vals_common, "name": art["name"]})
                print(f"created {post.id} {art['seo_name']}")
            else:
                post.write(vals_common)
                print(f"update shell {post.id} {art['seo_name']}")

            set_trans(post, "name", art["name"])
            set_trans(post, "subtitle", art["subtitle"])
            set_trans(post, "seo_name", art["seo_name"])
            set_trans(post, "content", art["content"])
            set_trans(post, "teaser_manual", art["teaser"])
            set_trans(post, "website_meta_title", art["meta_title"])
            set_trans(post, "website_meta_description", art["meta_desc"])
            set_trans(post, "website_meta_keywords", art["meta_kw"])
            created.append((post, art))

        cr.commit()

        for post, art in created:
            post.invalidate_recordset()
            print(f"  {post.website_url}")

        # Homepage: show 6 latest posts (prefer those with real covers later)
        all_posts = Post.search(
            [("blog_id", "=", blog.id), ("is_published", "=", True)],
            order="post_date desc, id desc",
            limit=6,
        )
        cards = []
        for p in all_posts:
            title = p.with_context(lang="ru_RU").name or ""
            teaser = p.with_context(lang="ru_RU").teaser_manual or p.with_context(lang="ru_RU").subtitle or ""
            url = (p.website_url or f"/blog/{p.id}").replace("&", "&amp;")
            # cover img from properties
            img = None
            try:
                props = json.loads(p.cover_properties or "{}")
                bg = props.get("background-image") or ""
                m = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", bg)
                if m and "website_blog/static" not in m.group(1):
                    img = m.group(1)
            except Exception:
                pass
            tags = p.tag_ids[:1]
            tag = tags[0].with_context(lang="ru_RU").name if tags else "советы"
            cards.append(
                card_html(
                    str(title).replace("&", "&amp;"),
                    str(teaser).replace("&", "&amp;")[:180],
                    url,
                    str(tag),
                    img,
                )
            )

        section = f"""
<section class="s_pepito_blog pt64 pb64 o_colored_level" data-snippet="s_text_block" data-name="Советы кинолога" style="background:#FBF3E8;">
  <div class="container">
    <div class="row mb-4 align-items-end">
      <div class="col-lg-8">
        <p class="text-uppercase small fw-semibold mb-2" style="color:#C45C26;letter-spacing:0.08em;">Журнал Pepito</p>
        <h2 class="mb-2" style="color:#1A0A00;font-family:'Playfair Display',serif;font-weight:700;">Советы кинолога</h2>
        <p class="mb-0" style="color:#5A3E28;max-width:36rem;">Поведение, щенки, лакомства и AI‑кинолог — коротко и по делу.</p>
      </div>
      <div class="col-lg-4 text-lg-end mt-3 mt-lg-0">
        <a href="/blog" class="btn btn-secondary">Все статьи</a>
      </div>
    </div>
    <div class="row g-4">
      {''.join(cards)}
    </div>
  </div>
</section>
"""
        section = re.sub(r"\n\s*", "\n", section).strip() + "\n"
        cr.execute("SELECT arch_db FROM ir_ui_view WHERE id = 554")
        arch_db = cr.fetchone()[0]
        if isinstance(arch_db, str):
            arch_db = json.loads(arch_db)
        new_arch = {}
        for lang, html in arch_db.items():
            if not isinstance(html, str):
                new_arch[lang] = html
                continue
            h = re.sub(r'<section class="s_pepito_blog[\s\S]*?</section>\s*', "", html)
            marker = '<section class="s_cta_box'
            if marker in h:
                h = h.replace(marker, section + marker, 1)
            new_arch[lang] = h
        cr.execute(
            "UPDATE ir_ui_view SET arch_db = %s::jsonb, write_date = (now() at time zone 'UTC') WHERE id = 554",
            [json.dumps(new_arch, ensure_ascii=False)],
        )
        cr.commit()
        print("homepage refreshed")
        print("DONE")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
