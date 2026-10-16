#!/usr/bin/env python3
"""Restore missing website /_custom/ SCSS attachments and force CSS rebuild."""
import base64
import sys

import odoo
from odoo import api, SUPERUSER_ID
from odoo.tools import config

config.parse_config(["-d", "odoo_user_pepito", "--http-port=8099", "--gevent-port=8098", "--stop-after-init"])
db = odoo.service.db.db_connect("odoo_user_pepito")
registry = odoo.registry("odoo_user_pepito")

files = {
    "/_custom/web.assets_frontend/website/static/src/scss/options/user_values.scss": """// Restored default hook
$o-user-website-values: map-merge($o-user-website-values, o-map-omit((
    // -- hook --
)));
""",
    "/_custom/web.assets_frontend/website/static/src/scss/options/colors/user_color_palette.scss": """
$o-user-color-palette: map-merge($o-user-color-palette, o-map-omit((
    // -- hook --
)));
""",
    "/_custom/web.assets_frontend/website/static/src/scss/options/colors/user_theme_color_palette.scss": """
$o-user-theme-color-palette: map-merge($o-user-theme-color-palette, o-map-omit((
    // -- hook --
)));
""",
    "/_custom/web.assets_frontend/website/static/src/scss/user_custom_rules.scss": r"""// Pepito custom rules + mobile menu fix (2026-08-06)
// NO backdrop-filter on header — breaks Bootstrap offcanvas (position:fixed).

#wrapwrap > header,
#wrapwrap > header .navbar,
#wrapwrap > header .o_header_mobile {
  background: #1A0A00 !important;
}

#wrapwrap > header .nav-link,
#wrapwrap > header .o_header_mobile .nav-link {
  color: #FDF6EE !important;
  font-weight: 700;
}

#wrapwrap > header .nav-link:hover,
#wrapwrap > header .nav-link.active {
  color: #F0A500 !important;
}

#wrapwrap > header .fa,
#wrapwrap > header .oi {
  color: #FDF6EE !important;
}

@media (max-width: 991.98px) {
  #wrapwrap > header .o_header_mobile.navbar {
    min-height: 64px !important;
  }

  #wrapwrap > header .o_header_mobile .navbar-brand.logo img,
  #wrapwrap > header .o_header_mobile .navbar-brand.logo span img {
    height: 52px !important;
    max-height: 52px !important;
  }

  #wrapwrap > header .o_header_mobile button[data-bs-toggle="offcanvas"] {
    min-width: 44px;
    min-height: 44px;
    display: inline-flex !important;
    align-items: center;
    justify-content: center;
    z-index: 1040;
  }

  #wrapwrap > header .o_header_mobile .navbar-toggler-icon {
    width: 1.6rem;
    height: 1.6rem;
    filter: invert(1) grayscale(1) brightness(2);
    opacity: 1 !important;
  }

  #wrapwrap > header #top_menu_collapse_mobile.offcanvas {
    position: fixed !important;
    top: 0 !important;
    right: 0 !important;
    bottom: 0 !important;
    z-index: 1055 !important;
    width: 85vw !important;
    max-width: 400px !important;
    height: 100vh !important;
    background-color: #fff !important;
    visibility: hidden;
    transform: translateX(100%);
    transition: transform 0.3s ease, visibility 0.3s ease;
    overflow-y: auto;
  }

  #wrapwrap > header #top_menu_collapse_mobile.offcanvas.show,
  #wrapwrap > header #top_menu_collapse_mobile.offcanvas.showing {
    visibility: visible !important;
    transform: none !important;
    display: flex !important;
    flex-direction: column !important;
  }

  header.o_transformed_not_affixed #top_menu_collapse_mobile.show,
  header.o_transformed_not_affixed #top_menu_collapse_mobile.showing {
    display: flex !important;
  }

  body .offcanvas-backdrop {
    z-index: 1050 !important;
  }

  #wrapwrap > header #top_menu_collapse_mobile .nav-link {
    color: #1A0A00 !important;
  }
  #wrapwrap > header #top_menu_collapse_mobile .nav-link.active,
  #wrapwrap > header #top_menu_collapse_mobile .nav-link:hover {
    color: #C8411A !important;
  }
}
""",
}

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    Att = env["ir.attachment"]
    for url, content in files.items():
        name = url.rsplit("/", 1)[-1]
        existing = Att.search([("url", "=", url)])
        datas = base64.b64encode(content.encode("utf-8"))
        vals = {
            "name": name,
            "type": "binary",
            "mimetype": "text/scss",
            "datas": datas,
            "url": url,
            "public": True,
        }
        # website_id if multi-website
        if "website_id" in Att._fields:
            website = env["website"].search([], limit=1)
            if website:
                vals["website_id"] = website.id
        if existing:
            existing.write({"datas": datas, "public": True})
            print("updated", url, existing.ids)
        else:
            rec = Att.create(vals)
            print("created", url, rec.id)

    env.registry.clear_cache("assets")
    broken = Att.search(
        ["|", ("url", "ilike", "assets_frontend.min.css"), ("name", "ilike", "assets_frontend.min.css")]
    )
    print("unlink broken css", broken.mapped("url"))
    broken.unlink()
    cr.commit()
    print("OK")
