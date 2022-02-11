from odoo import api
from odoo import fields
from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.onchange("membership_state")
    def _add_to_group(self):
        current_record = str(self.id).split("_")[1]
        user = self.env["res.users"].sudo().search([
            ('partner_id', '=', int(current_record))
        ])
        group = self.env["res.groups"].sudo().search([
            ('membership_group', '=', True)
        ])
        if user and group:
            if self.membership_state in ('paid', 'invoiced', 'free'):
                already_in_group = self.env["res.groups"].sudo().search([
                    ('id', '=', group.id),
                    ('users', 'in', user.ids),
                ])
                if not already_in_group:
                    group.sudo().write({"users": [(4, user.id)]})
            else:
                group.sudo().write({"users": [(3, user.id)]})
