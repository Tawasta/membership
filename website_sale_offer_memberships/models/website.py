from odoo import fields, models


class Website(models.Model):
    _inherit = "website"

    offer_membership_text = fields.Html(
        string="Website sale: offer membership", readonly=False, translate=True
    )
