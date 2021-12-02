from odoo import models, fields


class ContractContract(models.Model):
    _inherit = "contract.contract"

    note = fields.Html('Terms and conditions')
