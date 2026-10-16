#!/usr/bin/env python3
"""Fix blog translated fields (names, seo, content) + homepage block links."""
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

# Reuse article definitions by importing seed module
sys.path.insert(0, "/tmp")
from seed_blog_articles import ARTICLES, HOMEPAGE_SECTION, card_html, cover, COVERS  # noqa: E402


def set_trans(env, record, field: str, value: str) -> None:
    """Write a translated char/html field as plain string for ru + en."""
    for lang in ("ru_RU", "en_US"):
        record.with_context(lang=lang).write({field: value})


def main() -> int:
    registry = odoo.modules.registry.Registry.new("odoo_user_pepito")
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})

        blog = env["blog.blog"].browse(1)
        set_trans(env, blog, "name", "Советы кинолога")
        set_trans(env, blog, "subtitle", "Поведение, лакомства и AI‑кинолог Pepito")
        set_trans(env, blog, "seo_name", "sovety-kinologa")
        set_trans(env, blog, "website_meta_title", "Советы кинолога | Pepito Pet")
        set_trans(
            env,
            blog,
            "website_meta_description",
            "Практичные статьи о дрессировке, щенках и натуральных лакомствах. Блог Pepito и AI‑кинолог в Telegram.",
        )
        blog.write({"cover_properties": cover(COVERS[0], "0.5"), "active": True})
        print("blog fixed")

        Post = env["blog.post"]
        posts_out = []
        for art in ARTICLES:
            # find by id range or content match
            post = None
            for p in Post.search([("blog_id", "=", 1)]):
                # match seo intent
                if art["seo_name"] in str(p.seo_name) or art["seo_name"].replace("-", "") in str(
                    p.seo_name
                ).replace("-", ""):
                    post = p
                    break
                nm = str(p.with_context(lang="ru_RU").name)
                if art["name"][:20] in nm or "tyanet" in str(p.seo_name):
                    if art["seo_name"].split("-")[0] in str(p.seo_name) or art["name"][:15] in nm:
                        post = p
                        break
            if not post:
                # fallback: order by id and zip
                continue

            # Better match: by order of articles vs posts ordered by id
            pass

        posts = Post.search([("blog_id", "=", 1)], order="id asc")
        if len(posts) != len(ARTICLES):
            print(f"WARN posts={len(posts)} articles={len(ARTICLES)}")

        for post, art in zip(posts, ARTICLES):
            set_trans(env, post, "name", art["name"])
            set_trans(env, post, "subtitle", art["subtitle"])
            set_trans(env, post, "seo_name", art["seo_name"])
            set_trans(env, post, "content", art["content"])
            set_trans(env, post, "teaser_manual", art["teaser"])
            set_trans(env, post, "website_meta_title", art["meta_title"])
            set_trans(env, post, "website_meta_description", art["meta_desc"])
            set_trans(env, post, "website_meta_keywords", art["meta_kw"])
            post.write(
                {
                    "is_published": True,
                    "active": True,
                    "is_seo_optimized": True,
                    "author_name": "Pepito · AI‑кинолог",
                    "cover_properties": cover(art["cover"]),
                }
            )
            posts_out.append((post, art))
            print(f"fixed post {post.id}: {art['seo_name']}")

        cr.commit()

        # Invalidate website url computation - recompute
        for post, art in posts_out:
            post.invalidate_recordset()
        for post, art in posts_out:
            url = post.website_url
            print(f"  url {post.id}: {url}")

        # Homepage
        cards = []
        for post, art in posts_out:
            url = (post.website_url or f"/blog/{post.id}").replace("&", "&amp;")
            cards.append(
                card_html(
                    art["name"].replace("&", "&amp;"),
                    art["teaser"].replace("&", "&amp;"),
                    url,
                    art["tags"][0],
                )
            )
        section = HOMEPAGE_SECTION.format(cards="".join(cards))
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
            h = html
            h = re.sub(
                r'<section class="s_pepito_blog[\s\S]*?</section>\s*',
                "",
                h,
            )
            marker = '<section class="s_cta_box'
            if marker in h:
                h = h.replace(marker, section + marker, 1)
            new_arch[lang] = h
            print(f"homepage {lang}: pepito_blog={'s_pepito_blog' in h} len={len(h)}")
        cr.execute(
            "UPDATE ir_ui_view SET arch_db = %s::jsonb, write_date = (now() at time zone 'UTC') WHERE id = 554",
            [json.dumps(new_arch, ensure_ascii=False)],
        )
        cr.commit()
        try:
            env.registry.clear_cache()
        except Exception:
            pass
        print("DONE")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
