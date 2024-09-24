import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    add_memberships = fields.Boolean(
        string="Add members to this channel", default=False
    )

    @api.model
    def create(self, vals):
        record = super(SlideChannel, self).create(vals)
        if vals.get("add_memberships"):
            group = (
                self.env["res.groups"].sudo().search([("membership_group", "=", True)])
            )
            for user in group.users:
                if user.partner_id.subscription_ids.filtered(
                    lambda s: s.stage_id.type == "in_progress"
                ):
                    record._action_add_members(user.partner_id)
        return record

    def write(self, vals):
        record = super(SlideChannel, self).write(vals)
        if vals.get("add_memberships"):
            group = (
                self.env["res.groups"].sudo().search([("membership_group", "=", True)])
            )
            for user in group.users:
                if user.partner_id.subscription_ids.filtered(
                    lambda s: s.stage_id.type == "in_progress"
                ):
                    record._action_add_members(user.partner_id)
        return record
