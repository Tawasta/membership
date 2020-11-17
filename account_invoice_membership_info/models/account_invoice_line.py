from odoo import fields
from odoo import models


class AccountInvoiceLine(models.Model):

    _inherit = "account.invoice.line"

    membership_line_ids = fields.One2many(
        comodel_name="membership.membership_line", inverse_name="account_invoice_line",
    )
