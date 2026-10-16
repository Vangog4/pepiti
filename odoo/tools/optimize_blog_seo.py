#!/usr/bin/env python3
"""SEO hard-pass for all Pepito blog posts, tags, hub, sitemap base URL."""
from __future__ import annotations

import json
import re
import sys

sys.path.insert(0, "/usr/lib/python3/dist-packages")

import odoo  # noqa: E402
import odoo.api  # noqa: E402
import odoo.modules.registry  # noqa: E402
from odoo.tools import config  # noqa: E402

config.parse_config(
    ["--config", "/etc/odoo/odoo.conf", "--database", "odoo_user_pepito", "--no-http"]
)

PUBLIC = "https://pepitopet.ru"

# Ideal SEO pack per post id
SEO = {
    6: {
        "seo_name": "sobaka-tyanet-povodok",
        "title": "Собака тянет поводок: 3 шага без рывков | Pepito",
        "desc": "Собака тянет поводок? Стоп при натяжении, смена направления и награда у ноги — план на 10–15 минут в день. Без рывков. Советы AI‑кинолога Pepito.",
        "kw": "собака тянет поводок, дрессировка собаки, прогулка с собакой, не тянуть поводок, кинолог, Pepito",
        "subtitle": "Спокойная прогулка без рывков — практика 10–15 минут в день",
    },
    7: {
        "seo_name": "lakomstva-dlya-shchenka",
        "title": "Лакомства для щенка: как выбрать безопасно | Pepito",
        "desc": "Какие сушёные лакомства подходят щенку 2–12 мес: размер «в один укус», мягкость, состав без соли. Чеклист и ошибки. Pepito Pet.",
        "kw": "лакомства для щенка, сушёные лакомства щенку, чем наградить щенка, натуральные лакомства, Pepito",
        "subtitle": "Размер, жёсткость и частота — чеклист для щенков 2–12 месяцев",
    },
    8: {
        "seo_name": "sobaka-laet-na-gostey",
        "title": "Собака лает на гостей: план на 7 дней | Pepito",
        "desc": "Собака лает на гостей и звонок? Коврик «место», репетиции и спокойный сценарий у двери — план на 7 дней без крика. AI‑кинолог Pepito.",
        "kw": "собака лает на гостей, лай на звонок, успокоить собаку дома, дрессировка лая, Pepito",
        "subtitle": "От «охранника у двери» к спокойному приветствию — без наказаний",
    },
    9: {
        "seo_name": "dolgoigrayushchie-lakomstva",
        "title": "Долгоиграющие лакомства: когда давать | Pepito",
        "desc": "Долгоиграющие лакомства после прогулки и «один дома»: рубец, трахея, размер куска и правила безопасности. Когда жевание помогает. Pepito.",
        "kw": "долгоиграющие лакомства, жевательные лакомства собаке, рубец сушёный, трахея, собака одна дома, Pepito",
        "subtitle": "Жевание как инструмент: смена режима, «один дома», после прогулки",
    },
    10: {
        "seo_name": "ai-kinolog-pepito-kak-polzovatsya",
        "title": "AI‑кинолог Pepito в Telegram: как пользоваться",
        "desc": "Как пользоваться AI‑кинологом @pepitopetbot: онбординг питомца, free 5 запросов/день, Premium Stars, планы и голосовые. Гид Pepito.",
        "kw": "AI кинолог, телеграм бот для собак, pepitopetbot, дрессировка онлайн, Pepito",
        "subtitle": "Онбординг, лимиты free/premium, планы и голос — короткий гид",
    },
    11: {
        "seo_name": "sobaka-gryzyot-mebel",
        "title": "Собака грызёт мебель и плинтуса: что делать | Pepito",
        "desc": "Собака грызёт мебель и плинтуса? Разбираем скуку, зубы и тревогу. Легальный chew, зона доступа и режим до ухода. Советы Pepito.",
        "kw": "собака грызёт мебель, грызёт плинтус, щенок грызёт, долгоиграющие лакомства, один дома, Pepito",
        "subtitle": "Скука, тревога или смена зубов — легальная альтернатива до «ремонта»",
    },
    12: {
        "seo_name": "pervaya-progulka-shchenka",
        "title": "Первая прогулка щенка: чеклист на 14 дней | Pepito",
        "desc": "Первая прогулка щенка: 5–10 минут, тихий двор, мелкие награды и без перегруза стимулами. Чеклист на 14 дней от Pepito Pet.",
        "kw": "первая прогулка щенка, щенок гулять, социализация щенка, лакомства на прогулке, Pepito",
        "subtitle": "Короткие выходы, безопасные места и награды — без марафона в первый день",
    },
    13: {
        "seo_name": "lakomstva-na-dressirovke-ne-perekormit",  # keep URL stable
        "title": "Лакомства на дрессировке: как не перекормить | Pepito",
        "desc": "Лакомства на дрессировке без перекорма: крошки vs долгоиграющий chew, доля в рационе и размер «в один укус». Гайд Pepito Pet.",
        "kw": "лакомства на дрессировке, сколько лакомств собаке, награда за команду, не перекормить собаку, Pepito",
        "subtitle": "Крошки vs жевание: таблица «когда что» и доля в рационе",
    },
    14: {
        "seo_name": "komanda-ko-mne-na-ulitse",  # keep URL stable
        "title": "Команда «ко мне» на улице: как научить | Pepito",
        "desc": "Собака не подходит «ко мне» на улице? Recall по цепочке: комната → двор → улица, long line и high-value награды. Pepito.",
        "kw": "команда ко мне, recall собака, собака не подходит, подзыв собаки, дрессировка на улице, Pepito",
        "subtitle": "Надёжный подход: цепочка сложности и страховка на поводке",
    },
    15: {
        "seo_name": "nedelya-s-ai-kinologom",
        "title": "Неделя с AI‑кинологом: план вопросов | Pepito",
        "desc": "Неделя с AI‑кинологом Pepito: что писать боту каждый день — онбординг, план, фидбек и прогресс. Free и Premium Stars.",
        "kw": "AI кинолог, pepito бот, телеграм кинолог, план дрессировки, pepitopetbot, Pepito",
        "subtitle": "Roadmap диалогов — от онбординга до недельного плана",
    },
}

# Related internal links by post id (seo path slug + id)
RELATED = {
    6: [14, 12, 13],
    7: [12, 13, 9],
    8: [11, 15, 6],
    9: [11, 13, 7],
    10: [15, 6, 8],
    11: [9, 8, 12],
    12: [7, 6, 14],
    13: [7, 9, 6],
    14: [6, 12, 15],
    15: [10, 6, 14],
}

TAGS = {
    "поведение": {
        "seo_name": "povedenie",
        "title": "Поведение собак — статьи | Pepito",
        "desc": "Статьи о поведении: поводок, лай, грызение, команда «ко мне». Практичные советы AI‑кинолога Pepito.",
        "kw": "поведение собак, дрессировка, кинолог, Pepito",
    },
    "прогулка": {
        "seo_name": "progulka",
        "title": "Прогулка с собакой — советы | Pepito",
        "desc": "Прогулка и поводок, первая улица щенка, подзыв. Журнал Pepito.",
        "kw": "прогулка с собакой, поводок, щенок на улице, Pepito",
    },
    "щенок": {
        "seo_name": "shchenok",
        "title": "Щенок: лакомства и прогулки | Pepito",
        "desc": "Всё для щенка: лакомства, первая прогулка, безопасные награды. Pepito.",
        "kw": "щенок, лакомства для щенка, прогулка щенка, Pepito",
    },
    "лакомства": {
        "seo_name": "lakomstva",
        "title": "Сушёные лакомства для собак | Pepito",
        "desc": "Как выбирать и давать сушёные лакомства: щенкам, на дрессировке, долгоиграющие. Pepito.",
        "kw": "сушёные лакомства, лакомства для собак, натуральные лакомства, Pepito",
    },
    "дом": {
        "seo_name": "dom",
        "title": "Собака дома: лай, жевание, режим | Pepito",
        "desc": "Домашние сценарии: гости, мебель, спокойствие. Советы Pepito.",
        "kw": "собака дома, лай, грызёт мебель, Pepito",
    },
    "ai-кинолог": {
        "seo_name": "ai-kinolog",
        "title": "AI‑кинолог Pepito — статьи и гиды",
        "desc": "Как пользоваться AI‑кинологом в Telegram и вести программу тренировок. Pepito.",
        "kw": "AI кинолог, pepitopetbot, телеграм, Pepito",
    },
    "гайд": {
        "seo_name": "gaid",
        "title": "Гайды Pepito: бот и лакомства",
        "desc": "Практические гайды по боту и использованию лакомств. Pepito Pet.",
        "kw": "гайд, pepito, дрессировка, лакомства",
    },
    "тренировка": {
        "seo_name": "trenirovka",
        "title": "Тренировка собак — статьи | Pepito",
        "desc": "Упражнения и планы тренировок для собак. Журнал Pepito.",
        "kw": "тренировка собак, упражнения, Pepito",
    },
}


def set_trans(rec, field: str, value: str) -> None:
    for lang in ("ru_RU", "en_US"):
        rec.with_context(lang=lang).write({field: value})


def strip_related_block(html: str) -> str:
    if not html:
        return html
    return re.sub(
        r'<section class="pepito-seo-related"[\s\S]*?</section>\s*',
        "",
        html,
        count=1,
    )


def related_block(env, post_id: int, related_ids: list[int]) -> str:
    Post = env["blog.post"]
    items = []
    for rid in related_ids:
        p = Post.browse(rid)
        if not p.exists() or not p.is_published:
            continue
        title = p.with_context(lang="ru_RU").name or ""
        url = p.website_url or f"/blog/{rid}"
        items.append(
            f'<li style="margin-bottom:0.4rem;"><a href="{url}" style="color:#C45C26;">{title}</a></li>'
        )
    if not items:
        return ""
    return f"""
<section class="pepito-seo-related mt-5 mb-3 p-4 rounded-3" style="background:#fff;border:1px solid rgba(26,10,0,0.08);">
  <h2 style="color:#1A0A00;font-family:'Playfair Display',serif;font-size:1.35rem;margin-bottom:0.75rem;">Читайте также</h2>
  <ul style="margin:0;padding-left:1.2rem;color:#5A3E28;">
    {''.join(items)}
  </ul>
  <p class="mb-0 mt-3 small"><a href="/blog" style="color:#C45C26;">Все статьи журнала Pepito →</a>
  · <a href="https://t.me/pepitopetbot" target="_blank" rel="noopener" style="color:#C45C26;">AI‑кинолог в Telegram →</a></p>
</section>
"""


def main() -> int:
    registry = odoo.modules.registry.Registry.new("odoo_user_pepito")
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        # 1) Public base URL + website domain (sitemap + absolute URLs)
        ICP = env["ir.config_parameter"].sudo()
        ICP.set_param("web.base.url", PUBLIC)
        ICP.set_param("web.base.url.freeze", "True")
        website = env["website"].browse(1)
        website.write({"domain": PUBLIC})
        robots = (
            "User-agent: *\n"
            "Allow: /\n"
            "Disallow: /web\n"
            "Disallow: /web/\n"
            "Disallow: /my\n"
            "Disallow: /my/\n"
            f"Sitemap: {PUBLIC}/sitemap.xml\n"
        )
        website.write({"robots_txt": robots})
        print(f"base.url + domain + robots → {PUBLIC}")

        # 2) Blog hub
        blog = env["blog.blog"].browse(1)
        set_trans(blog, "name", "Советы кинолога")
        set_trans(blog, "subtitle", "Поведение, лакомства, щенки и AI‑кинолог Pepito")
        set_trans(blog, "seo_name", "sovety-kinologa")
        set_trans(blog, "website_meta_title", "Советы кинолога — журнал Pepito Pet")
        set_trans(
            blog,
            "website_meta_description",
            "Практичные статьи о дрессировке, щенках и натуральных лакомствах. AI‑кинолог в Telegram и магазин pepitopet.ru.",
        )
        set_trans(
            blog,
            "website_meta_keywords",
            "советы кинолога, дрессировка собак, лакомства для собак, AI кинолог, Pepito, pepitopet",
        )
        print("blog hub SEO ok")

        # 3) Tags
        Tag = env["blog.tag"]

        def tag_label(t) -> str:
            return str(t.with_context(lang="ru_RU").name or t.name or "")

        for t in Tag.search([]):
            label = tag_label(t).lower()
            pack = TAGS.get(label)
            if not pack:
                continue
            set_trans(t, "seo_name", pack["seo_name"])
            set_trans(t, "website_meta_title", pack["title"])
            set_trans(t, "website_meta_description", pack["desc"])
            set_trans(t, "website_meta_keywords", pack["kw"])
            print(f"  tag {label} seo")

        # 4) Posts
        Post = env["blog.post"]
        for pid, pack in SEO.items():
            post = Post.browse(pid)
            if not post.exists():
                print(f"skip missing {pid}")
                continue
            set_trans(post, "seo_name", pack["seo_name"])
            set_trans(post, "website_meta_title", pack["title"])
            set_trans(post, "website_meta_description", pack["desc"])
            set_trans(post, "website_meta_keywords", pack["kw"])
            set_trans(post, "subtitle", pack["subtitle"])

            # Absolute OG image
            og = post.website_meta_og_img or ""
            m = re.search(r"/web/image/(\d+)", og)
            if not m:
                try:
                    props = json.loads(post.cover_properties or "{}")
                    bg = props.get("background-image") or ""
                    m = re.search(r"/web/image/(\d+)", bg)
                except Exception:
                    m = None
            if m:
                post.write({"website_meta_og_img": f"{PUBLIC}/web/image/{m.group(1)}"})

            # Related block in content
            content = post.with_context(lang="ru_RU").content or ""
            if isinstance(content, dict):
                content = content.get("ru_RU") or content.get("en_US") or ""
            content = strip_related_block(str(content))
            rel = related_block(env, pid, RELATED.get(pid, []))
            # insert before final CTA section or at end of outer container
            if 'class="mt-5 mb-4 p-4 rounded-3"' in content and "Нужен персональный план" in content:
                # before last CTA box
                idx = content.rfind("<section class=\"mt-5 mb-4")
                if idx == -1:
                    idx = content.rfind("<section class='mt-5 mb-4")
                if idx != -1:
                    content = content[:idx] + rel + content[idx:]
                else:
                    content = content.replace("</div>\n", rel + "</div>\n", 1) if content.endswith("</div>") else content + rel
            else:
                content = content + rel

            set_trans(post, "content", content)
            post.write(
                {
                    "is_published": True,
                    "active": True,
                    "author_name": "Pepito · AI‑кинолог",
                }
            )

            tlen = len(pack["title"])
            dlen = len(pack["desc"])
            print(f"post {pid}: title={tlen}c desc={dlen}c slug={pack['seo_name']}")

        cr.commit()

        # Recompute is_seo_optimized by touching fields (stored compute)
        for pid in SEO:
            p = Post.browse(pid)
            if p.exists():
                p._compute_is_seo_optimized()
        blog._compute_is_seo_optimized()
        for t in Tag.search([]):
            t._compute_is_seo_optimized()
        cr.commit()

        try:
            env.registry.clear_cache()
        except Exception:
            pass

        print("DONE")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
