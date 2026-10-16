#!/usr/bin/env python3
"""Upload generated blog covers and attach to blog.post cover_properties."""
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

# post_id -> filename under /tmp/blog_covers/
MAPPING = {
    6: ("3.jpg", "cover-tyanet-povodok.jpg"),
    7: ("2.jpg", "cover-shchenok-lakomstva.jpg"),
    8: ("4.jpg", "cover-laet-na-gostey.jpg"),
    9: ("5.jpg", "cover-dolgoigrayushchie.jpg"),
    10: ("1.jpg", "cover-ai-kinolog.jpg"),
}

SRC_DIR = "/tmp/blog_covers"


def cover_props(attachment_id: int, opacity: str = "0.35") -> str:
    url = f"/web/image/{attachment_id}"
    return json.dumps(
        {
            "background-image": f"url('{url}')",
            "resize_class": "o_record_has_cover o_half_screen_height",
            "opacity": opacity,
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
        attached = {}  # post_id -> (att_id, url)

        for post_id, (src_name, public_name) in MAPPING.items():
            path = os.path.join(SRC_DIR, src_name)
            if not os.path.isfile(path):
                print(f"MISSING {path}")
                continue
            with open(path, "rb") as f:
                data = base64.b64encode(f.read()).decode()

            post = Post.browse(post_id)
            if not post.exists():
                print(f"no post {post_id}")
                continue

            # remove previous covers we created
            old = Att.search(
                [
                    ("name", "=", public_name),
                    ("res_model", "=", "blog.post"),
                    ("res_id", "=", post_id),
                ]
            )
            if old:
                old.unlink()

            att = Att.create(
                {
                    "name": public_name,
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
            attached[post_id] = (att.id, f"/web/image/{att.id}")
            print(f"post {post_id} <- att {att.id} ({public_name})")

        cr.commit()

        # Refresh homepage cards with cover thumbnails
        if attached:
            cr.execute("SELECT arch_db FROM ir_ui_view WHERE id = 554")
            arch_db = cr.fetchone()[0]
            if isinstance(arch_db, str):
                arch_db = json.loads(arch_db)

            # rebuild section with images
            cards = []
            meta = {
                6: ("Собака тянет поводок: 3 шага, которые работают",
                    "Рывок поводка — сигнал, что цель впереди важнее вас. Меняем правила игры: стоп, поворот, награда у ноги.",
                    "поведение"),
                7: ("Лакомства для щенка: как выбрать без вреда",
                    "Щенку важны мягкость, размер «в один укус» и отсутствие специй. Жёсткие кости и огромные трубки — на потом.",
                    "щенок"),
                8: ("Собака лает на гостей: план на 7 дней",
                    "Лай на звонок — часто смесь возбуждения и охраны. Учим альтернативу: место → тишина → награда.",
                    "поведение"),
                9: ("Долгоиграющие лакомства: когда они спасают нервы",
                    "Жевание снижает возбуждение. Правильный «долгоиграющий» кусок — не скука, а гигиена нервной системы.",
                    "лакомства"),
                10: ("AI‑кинолог Pepito: как пользоваться ботом с умом",
                     "Бот силён, когда знает питомца. 2 минуты онбординга экономят 20 минут бессмысленных общих советов.",
                     "ai-кинолог"),
            }
            for post_id in (6, 7, 8, 9, 10):
                post = Post.browse(post_id)
                url = (post.website_url or f"/blog/{post_id}").replace("&", "&amp;")
                title, teaser, tag = meta[post_id]
                img = attached[post_id][1]
                cards.append(
                    f"""
      <div class="col-md-6 col-lg-4">
        <a href="{url}" class="text-decoration-none d-block h-100" style="color:inherit;">
          <div class="h-100 border-0 overflow-hidden" style="border-radius:20px;background:#fff;box-shadow:0 8px 32px rgba(26,10,0,0.08);transition:transform .15s ease;">
            <div style="height:180px;background:url('{img}') center/cover no-repeat;background-color:#FBF3E8;"></div>
            <div style="padding:22px 22px 24px;">
              <span class="d-inline-block mb-2 small fw-semibold" style="color:#C45C26;background:rgba(196,92,38,0.10);padding:4px 10px;border-radius:999px;">{tag}</span>
              <h3 class="h5 mb-2" style="color:#1A0A00;font-family:'Playfair Display',serif;font-weight:700;line-height:1.35;">{title}</h3>
              <p class="mb-3 small" style="color:#5A3E28;line-height:1.55;">{teaser}</p>
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
        <p class="mb-0" style="color:#5A3E28;max-width:36rem;">Поведение, щенки, лакомства и AI‑кинолог — коротко и по делу. Без воды и без «ветеринарных диагнозов».</p>
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
                marker = '<section class="s_cta_box'
                if marker in h:
                    h = h.replace(marker, section + marker, 1)
                new_arch[lang] = h
            cr.execute(
                "UPDATE ir_ui_view SET arch_db = %s::jsonb, write_date = (now() at time zone 'UTC') WHERE id = 554",
                [json.dumps(new_arch, ensure_ascii=False)],
            )
            cr.commit()
            print("homepage cards updated with cover images")

        try:
            env.registry.clear_cache()
        except Exception:
            pass
        print("DONE")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
