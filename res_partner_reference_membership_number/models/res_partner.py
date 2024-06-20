from odoo import fields, models


class Partner(models.Model):
    _inherit = "res.partner"

    ref = fields.Char(string="Membership Number")
