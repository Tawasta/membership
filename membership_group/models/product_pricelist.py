from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    membership_pricelist = fields.Boolean(string="Membership pricelist")

    is_public = fields.Boolean(string="Public/Default pricelist")


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    additional_membership_price = fields.Boolean(
        string="Additional membership price", default=False
    )
