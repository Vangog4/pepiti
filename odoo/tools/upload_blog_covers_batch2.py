#!/usr/bin/env python3
"""Attach batch-2 covers and refresh homepage with latest 6 posts + images."""
from __future__ import annotations

import base64
import json
import os
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

SRC = "/tmp/blog_covers"
# post_id -> (file, public name)
MAPPING = {
    11: ("7.jpg", "cover-gryzyot-mebel.jpg"),
    12: ("9.jpg", "cover-pervaya-progulka.jpg"),
    13: ("6.jpg", "cover-ne-perekormit.jpg"),
    14: ("8.jpg", "cover-ko-mne.jpg"),
    15: ("10.jpg", "cover-nedelya-ai.jpg"),
}


def cover_props(att_id: int) -> str:
    return json.dumps(
        {
            "background-image": f"url('/web/image/{att_id}')",
            "resize_class": "o_record_has_cover o_half_screen_height",
            "opacity": "0.35",
            "background_color_class": "o_cc o_cc5",
            "background_color_style": "",
        }
    )


def main() -> int:
    registry = odoo.modules.registry.Registry.new("odoo_user_pepito")
    with registry.cursor() as cr:
        env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
        Att = env["ir.attachment"]
        Post = env["blog.post"]

        for post_id, (fname, public) in MAPPING.items():
            path = os.path.join(SRC, fname)
            if not os.path.isfile(path):
                print("MISSING", path)
                continue
            data = base64.b64encode(open(path, "rb").read()).decode()
            post = Post.browse(post_id)
            if not post.exists():
                print("no post", post_id)
                continue
            old = Att.search(
                [("name", "=", public), ("res_model", "=", "blog.post"), ("res_id", "=", post_id)]
            )
            if old:
                old.unlink()
            att = Att.create(
                {
                    "name": public,
                    "type": "binary",
                    "datas": data,
                    "res_model": "blog.post",
                    "res_id": post_id,
                    "public": True,
                    "mimetype": "image/jpeg",
                }
            )
            post.write(
                {
                    "cover_properties": cover_props(att.id),
                    "website_meta_og_img": f"/web/image/{att.id}",
                }
            )
            print(f"post {post_id} <- att {att.id} ({public})")

        cr.commit()

        # Homepage: latest 6 with covers
        posts = Post.search(
            [("is_published", "=", True)], order="post_date desc, id desc", limit=6
        )
        cards = []
        for p in posts:
            title = str(p.with_context(lang="ru_RU").name or "")
            teaser = str(
                p.with_context(lang="ru_RU").teaser_manual
                or p.with_context(lang="ru_RU").subtitle
                or ""
            )[:180]
            url = (p.website_url or f"/blog/{p.id}").replace("&", "&amp;")
            img = None
            try:
                props = json.loads(p.cover_properties or "{}")
                bg = props.get("background-image") or ""
                m = re.search(r"url\(['\"]?([^'\")]+)['\"]?\)", bg)
                if m:
                    img = m.group(1)
            except Exception:
                pass
            tag = "советы"
            if p.tag_ids:
                tag = str(p.tag_ids[0].with_context(lang="ru_RU").name or tag)
            img_block = (
                f'<div style="height:180px;background:url(\'{img}\') center/cover no-repeat;background-color:#FBF3E8;"></div>'
                if img
                else ""
            )
            cards.append(
                f"""
      <div class="col-md-6 col-lg-4">
        <a href="{url}" class="text-decoration-none d-block h-100" style="color:inherit;">
          <div class="h-100 border-0 overflow-hidden" style="border-radius:20px;background:#fff;box-shadow:0 8px 32px rgba(26,10,0,0.08);">
            {img_block}
            <div style="padding:22px 22px 24px;">
              <span class="d-inline-block mb-2 small fw-semibold" style="color:#C45C26;background:rgba(196,92,38,0.10);padding:4px 10px;border-radius:999px;">{tag}</span>
              <h3 class="h5 mb-2" style="color:#1A0A00;font-family:'Playfair Display',serif;font-weight:700;line-height:1.35;">{title.replace('&','&amp;')}</h3>
              <p class="mb-3 small" style="color:#5A3E28;line-height:1.55;">{teaser.replace('&','&amp;')}</p>
              <span class="fw-semibold" style="color:#C45C26;">Читать →</span>
            </div>
          </div>
        </a>
      </div>"""
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
        try:
            env.registry.clear_cache()
        except Exception:
            pass
        print("homepage OK")
        print("DONE")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
