#!/usr/bin/env python3
import base64
import sys

sys.path.insert(0, "/usr/lib/python3/dist-packages")
import odoo
from odoo.tools import config

config.parse_config(
    ["--config", "/etc/odoo/odoo.conf", "--database", "odoo_user_pepito", "--no-http"]
)
import odoo.modules.registry

CUSTOM = r"""// Pepito custom rules + mobile menu (libsass-safe)
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
  #wrapwrap > header .o_header_mobile.navbar { min-height: 64px !important; }
  #wrapwrap > header .o_header_mobile .navbar-brand.logo img,
  #wrapwrap > header .o_header_mobile .navbar-brand.logo span img {
    height: 52px !important; max-height: 52px !important;
  }
  #wrapwrap > header .o_header_mobile button[data-bs-toggle="offcanvas"] {
    min-width: 44px; min-height: 44px; display: inline-flex !important;
    align-items: center; justify-content: center; z-index: 1040;
  }
  #wrapwrap > header .o_header_mobile .navbar-toggler-icon {
    width: 1.6rem; height: 1.6rem;
    filter: invert(1) grayscale(1) brightness(2); opacity: 1 !important;
  }
  #wrapwrap > header #top_menu_collapse_mobile.offcanvas {
    position: fixed !important; top: 0 !important; right: 0 !important; bottom: 0 !important;
    z-index: 1055 !important;
    width: 85vw !important;
    max-width: 400px !important;
    height: 100vh !important;
    background-color: #fff !important;
    visibility: hidden; transform: translateX(100%);
    transition: transform 0.3s ease, visibility 0.3s ease; overflow-y: auto;
  }
  #wrapwrap > header #top_menu_collapse_mobile.offcanvas.show,
  #wrapwrap > header #top_menu_collapse_mobile.offcanvas.showing {
    visibility: visible !important; transform: none !important;
    display: flex !important; flex-direction: column !important;
  }
  header.o_transformed_not_affixed #top_menu_collapse_mobile.show,
  header.o_transformed_not_affixed #top_menu_collapse_mobile.showing {
    display: flex !important;
  }
  body .offcanvas-backdrop { z-index: 1050 !important; }
  #wrapwrap > header #top_menu_collapse_mobile .nav-link { color: #1A0A00 !important; }
  #wrapwrap > header #top_menu_collapse_mobile .nav-link.active,
  #wrapwrap > header #top_menu_collapse_mobile .nav-link:hover { color: #C8411A !important; }
}
"""

hooks = {
    "/_custom/web.assets_frontend/website/static/src/scss/options/user_values.scss": """// hook
$o-user-website-values: map-merge($o-user-website-values, o-map-omit((
)));
""",
    "/_custom/web.assets_frontend/website/static/src/scss/options/colors/user_color_palette.scss": """
$o-user-color-palette: map-merge($o-user-color-palette, o-map-omit((
)));
""",
    "/_custom/web.assets_frontend/website/static/src/scss/options/colors/user_theme_color_palette.scss": """
$o-user-theme-color-palette: map-merge($o-user-theme-color-palette, o-map-omit((
)));
""",
    "/_custom/web.assets_frontend/website/static/src/scss/user_custom_rules.scss": CUSTOM,
}

reg = odoo.modules.registry.Registry.new("odoo_user_pepito")
with reg.cursor() as cr:
    env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
    Att = env["ir.attachment"]
    website = env["website"].search([], limit=1)
    for url, content in hooks.items():
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
        if "website_id" in Att._fields and website:
            vals["website_id"] = website.id
        if existing:
            existing.write({"datas": datas, "public": True, "mimetype": "text/scss"})
            print("upd", url, existing.ids)
        else:
            print("new", url, Att.create(vals).id)

    broken = Att.search(
        [
            "|",
            ("url", "ilike", "assets_frontend.min.css"),
            ("name", "ilike", "assets_frontend.min.css"),
        ]
    )
    print("unlink", broken.ids)
    broken.unlink()
    try:
        env.registry.clear_cache("assets")
    except Exception as e:
        print("cache", e)
    cr.commit()

    bundle = env["ir.qweb"]._get_asset_bundle("web.assets_frontend")
    css = bundle.css()
    raw = css.raw or b""
    print("css_len", len(raw))
    print("url", css.url)
    text = raw.decode("utf-8", "replace")
    if "css error" in text.lower() or "old style" in text.lower() or len(raw) < 20000:
        print("STILL BROKEN")
        print(text[:1500])
        raise SystemExit(1)
    print("has 1A0A00", "1A0A00" in text or "1a0a00" in text)
    print("has s_pepito_blog", "s_pepito_blog" in text)
    print("has Playfair", "Playfair" in text)
    print("CSS OK")
