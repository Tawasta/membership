from odoo import _, models


class AccountMove(models.Model):
    _inherit = "account.move"

    def write(self, vals):
        # Override to trigger permissions change when membership state changes
        res = super().write(vals)

        if "state" in vals:
            for record in self:
                msg = _(
                    "Compute membership permissions for {}".format(
                        record.partner_id.name
                    )
                )
                record.partner_id.with_delay(
                    description=msg
                )._compute_membership_permissions()

        return res
