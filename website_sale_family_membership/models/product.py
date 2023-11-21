from odoo import _, fields, models

class ProductAttribute(models.Model):
    _inherit = "product.attribute"

    family_members_rule = fields.Boolean(
        string="This rule tells how many family members will be added",
    )
