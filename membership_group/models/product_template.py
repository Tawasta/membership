from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    pricelist_id = fields.Many2one(comodel_name="product.pricelist", string="Pricelist")
