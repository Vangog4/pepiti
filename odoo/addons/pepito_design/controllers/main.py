from odoo import http
from odoo.addons.website.controllers.main import Website


class PepitoWebsiteSeo(Website):
    """Force https://pepitopet.ru in sitemap when reverse-proxy strips TLS scheme."""

    @http.route(
        "/sitemap.xml",
        type="http",
        auth="public",
        website=True,
        multilang=False,
        sitemap=False,
    )
    def sitemap_xml_index(self, **kwargs):
        response = super().sitemap_xml_index(**kwargs)
        try:
            data = response.get_data(as_text=True)
            if "pepitopet.ru" in data and "http://pepitopet.ru" in data:
                data = data.replace("http://pepitopet.ru", "https://pepitopet.ru")
                response.set_data(data)
                # bust wrong-scheme attachment cache on next rebuild
        except Exception:
            pass
        return response

    @http.route(
        ["/robots.txt"],
        type="http",
        auth="public",
        website=True,
        multilang=False,
        sitemap=False,
    )
    def robots(self, **kwargs):
        response = super().robots(**kwargs)
        try:
            data = response.get_data(as_text=True)
            if "pepitopet.ru" in data:
                data = data.replace("http://pepitopet.ru", "https://pepitopet.ru")
                # avoid duplicate sitemap lines
                lines = []
                seen_sitemap = False
                for line in data.splitlines():
                    if line.strip().lower().startswith("sitemap:"):
                        if seen_sitemap:
                            continue
                        seen_sitemap = True
                        lines.append("Sitemap: https://pepitopet.ru/sitemap.xml")
                    else:
                        lines.append(line)
                response.set_data("\n".join(lines) + "\n")
        except Exception:
            pass
        return response
