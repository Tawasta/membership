from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    free_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Free products",
    )

    membership_type = fields.Selection(
        [("company", "Company"), ("contact", "Contact")],
        string="Membership Type",
        default="contact",
        required=True,
    )
