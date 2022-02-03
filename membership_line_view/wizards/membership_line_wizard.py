from odoo import fields, models
from odoo.addons.membership.models.membership import STATE


class MembershipLineWizard(models.TransientModel):

    _name = "membership.line.wizard"
    _description = "Membership Line Wizard"

    membership_line_id = fields.Many2one(
        comodel_name="membership.membership_line",
        string="Membership line",
        required=True,
        index=True,
        ondelete="cascade",
    )

    override_state = fields.Selection(STATE, string="New membership status")

    def action_override_state(self):
        for record in self:
            record.membership_line_id.write({"state": record.override_state, "override_state": record.override_state})

