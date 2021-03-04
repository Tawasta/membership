from odoo import api
from odoo import fields
from odoo import models


class MembershipInvoice(models.TransientModel):
    _inherit = "membership.invoice"

    payment_term_id = fields.Many2one("account.payment.term", string="Payment Terms")
    date = fields.Date(string="Accounting Date")
    partner_bank_id = fields.Many2one(
        "res.partner.bank",
        string="Bank Account",
        domain=lambda self: [
            ("partner_id", "=", self.env.user.company_id.partner_id.id)
        ],
    )

    @api.multi
    def membership_invoice(self):
        res = super().membership_invoice()

        # It's not possible to override the datas that will be used to create
        # invoices. We'll need to change the values after the creation
        domain = res.get("domain")
        if domain:
            invoices = self.env["account.invoice"].search(domain)
            values = {}

            if self.payment_term_id:
                values["payment_term_id"] = self.payment_term_id.id
            if self.date:
                values["date"] = self.date
            if self.partner_bank_id:
                values["partner_bank_id"] = self.partner_bank_id.id

            if values:
                invoices.write(values)

        return res
