from odoo import models


class Partner(models.Model):

    _inherit = "res.partner"

    def assign_membership_group(self):
        # Search membership group and add user to it
        membership_group = (
            self.env["res.groups"]
            .sudo()
            .search([("membership_group", "=", True)], limit=1)
        )
        if membership_group:
            for record in self:
                for user in record.user_ids:
                    membership_group.sudo().write({"users": [(4, user.id)]})
