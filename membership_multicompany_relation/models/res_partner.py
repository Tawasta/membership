from odoo import fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    # Change the used term
    customer_of = fields.Many2many(
        string="Member of",
    )
