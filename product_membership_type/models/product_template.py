from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_type = fields.Selection(
        [("family", "Family"), ("contact", "Contact"), ("company", "Company")],
        string="Membership Type",
        default="contact",
        required=True,
    )
