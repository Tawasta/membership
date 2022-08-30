from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"

    def write(self, vals):
        print("==ACCOUNT MOVE WRITE====")
        print(vals)
        res = super().write(vals)
        if vals.get("state") and vals.get("state") == 'posted':
            is_membership = False

            for line in self.invoice_line_ids:
                if line.product_id.membership:
                    is_membership = True

            if is_membership:
                self.customer_contact_id._compute_membership_state()
