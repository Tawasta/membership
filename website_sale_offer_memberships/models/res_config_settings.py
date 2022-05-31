from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    website_sale_offer_membership_text = fields.Html(
        string="Website sale: offer membership",
        related="website_id.offer_membership_text",
        readonly=False,
        translate=True,
    )
