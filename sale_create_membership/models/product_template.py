from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    free_products_ids = fields.Many2many(
        "product.product",
        string="Free products",
    )

    membership_type = fields.Selection(
        [("company", "Company"), ("contact", "Contact")],
        string="Membership Type",
        default="contact",
        required=True,
    )
