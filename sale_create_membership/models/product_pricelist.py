from odoo import fields
from odoo import models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    membership_pricelist = fields.Boolean(string="Membership pricelist")
