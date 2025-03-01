from odoo import _, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _cron_update_membership(self):
        """Overwrite the cron and force using a queue"""
        partners = self.search([("membership_state", "in", ["invoiced", "paid"])])
        for partner in partners:
            # mark the field to be recomputed, and recompute it
            msg = _("Compute membership state for {}".format(partner.name))
            partner.with_delay(description=msg)._compute_membership_state()
