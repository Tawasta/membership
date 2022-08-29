from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    def _get_invoice_in_payment_state(self):
        res = super()._get_invoice_in_payment_state()

        if res == "paid":
            print(self)
            is_membership = False

            for line in self.invoice_line_ids:
                if line.product_id.membership:
                    is_membership = True

            if is_membership:
                self.customer_contact_id._compute_membership_state()

        return res
