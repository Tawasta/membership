from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    extra_products_ids = fields.Many2many(
        "product.product",
        string="Extra products",
    )

    membership_type = fields.Selection(
        [("family", "Family"), ("contact", "Contact")],
        string="Membership Type",
        default="contact",
        required=True,
    )
