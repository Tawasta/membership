from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    membership_contract_prorate = fields.Boolean(
        "Contract prorate",
        help="When purchasing new membership, "
        "prorate price according to an existing contract",
    )
