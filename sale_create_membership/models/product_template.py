from odoo import fields
from odoo import models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    free_products_ids = fields.Many2one(
        string="Free products", comodel_name="product.template"
    )
