#!/usr/bin/env python3
"""Fix homepage blog block: CSS broken by HTML-escaped quotes in style attrs.

Rebuilds s_pepito_blog with:
- <img> covers (not background:url with quotes)
- no single-quoted CSS
- 6 latest published posts
"""
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


def cover_src(post) -> str:
    og = post.website_meta_og_img or ""
    m = re.search(r"/web/image/\d+", og)
    if m:
        return m.group(0)
    try:
        props = json.loads(post.cover_properties or "{}")
        bg = props.get("background-image") or ""
        m = re.search(r"/web/image/\d+", bg)
        if m:
            return m.group(0)
    except Exception:
        pass
    return ""


def card(post, env) -> str:
    title = str(post.with_context(lang="ru_RU").name or "").replace("&", "&amp;")
    teaser = str(
        post.with_context(lang="ru_RU").teaser_manual
        or post.with_context(lang="ru_RU").subtitle
        or ""
    ).replace("&", "&amp;")[:160]
    url = (post.website_url or f"/blog/{post.id}").replace("&", "&amp;")
    tag = "советы"
    if post.tag_ids:
        tag = str(post.tag_ids[0].with_context(lang="ru_RU").name or tag).replace("&", "&amp;")
    img = cover_src(post)
    img_html = (
        f'<img src="{img}" alt="{title}" class="w-100" '
        f'style="height:180px;object-fit:cover;display:block;background-color:#FBF3E8;"/>'
        if img
        else '<div style="height:180px;background-color:#FBF3E8;"></div>'
    )
    return f"""
      <div class="col-md-6 col-lg-4">
        <a href="{url}" class="text-decoration-none d-block h-100" style="color:inherit;">
          <div class="h-100 border-0 overflow-hidden pepito-blog-card" style="border-radius:20px;background:#fff;box-shadow:0 8px 32px rgba(26,10,0,0.08);">
            {img_html}
            <div style="padding:22px 22px 24px;">
              <span class="d-inline-block mb-2 small fw-semibold" style="color:#C45C26;background:rgba(196,92,38,0.10);padding:4px 10px;border-radius:999px;">{tag}</span>
              <h3 class="h5 mb-2" style="color:#1A0A00;font-weight:700;line-height:1.35;">{title}</h3>
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
        Post = env["blog.post"]
        posts = Post.search(
            [("is_published", "=", True), ("active", "=", True)],
            order="post_date desc, id desc",
            limit=6,
        )
        cards = "".join(card(p, env) for p in posts)
        section = f"""
<section class="s_pepito_blog pt64 pb64 o_colored_level" data-snippet="s_text_block" data-name="Советы кинолога" style="background-color:#FBF3E8;">
  <div class="container">
    <div class="row mb-4 align-items-end">
      <div class="col-lg-8">
        <p class="text-uppercase small fw-semibold mb-2" style="color:#C45C26;letter-spacing:0.08em;">Журнал Pepito</p>
        <h2 class="mb-2" style="color:#1A0A00;font-weight:700;">Советы кинолога</h2>
        <p class="mb-0" style="color:#5A3E28;max-width:36rem;">Поведение, щенки, лакомства и AI-кинолог — коротко и по делу.</p>
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
        # compact whitespace but keep valid XML text
        section = re.sub(r"\n[ \t]+", "\n", section).strip() + "\n"

        cr.execute("SELECT arch_db FROM ir_ui_view WHERE id = 554")
        arch_db = cr.fetchone()[0]
        if isinstance(arch_db, str):
            arch_db = json.loads(arch_db)

        new_arch = {}
        for lang, html in arch_db.items():
            if not isinstance(html, str):
                new_arch[lang] = html
                continue
            h = re.sub(
                r'<section class="s_pepito_blog[\s\S]*?</section>\s*',
                "",
                html,
            )
            # also clean any residual broken entity styles from old inject near blog
            marker = '<section class="s_cta_box'
            if marker in h:
                h = h.replace(marker, section + marker, 1)
            else:
                raise SystemExit("cta marker not found — abort to avoid breaking homepage")
            # sanity: no &#39; inside our section
            if "s_pepito_blog" in h:
                part = h[h.find("s_pepito_blog") : h.find("s_pepito_blog") + 8000]
                if "&#39;" in part or "&#x27;" in part:
                    print("WARN still entities in blog section")
            new_arch[lang] = h

        # validate XML
        from lxml import etree

        for lang, html in new_arch.items():
            if isinstance(html, str):
                try:
                    etree.fromstring(html.encode("utf-8"))
                    print(f"XML ok {lang} len={len(html)}")
                except etree.XMLSyntaxError as e:
                    print(f"XML FAIL {lang}: {e}")
                    raise

        cr.execute(
            "UPDATE ir_ui_view SET arch_db = %s::jsonb, write_date = (now() at time zone 'UTC') WHERE id = 554",
            [json.dumps(new_arch, ensure_ascii=False)],
        )
        cr.commit()
        try:
            env.registry.clear_cache()
        except Exception:
            pass
        print("posts on homepage:", [(p.id, p.with_context(lang="ru_RU").name[:40]) for p in posts])
        print("DONE")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
