from odoo import models


class Website(models.Model):
    _inherit = "website"

    def get_base_url(self):
        """Force public HTTPS for production shop domain (sitemap / absolute links)."""
        for website in self:
            domain = (website.domain or "").lower()
            if "pepitopet.ru" in domain:
                return "https://pepitopet.ru"
        return super().get_base_url()
