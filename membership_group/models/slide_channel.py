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
        if vals.get("add_memberships") and vals.get("add_memberships") is True:
            group = (
                self.env["res.groups"].sudo().search([("membership_group", "=", True)])
            )
            for user in group.users:
                if (
                    user.partner_id.membership_state == "paid"
                    or user.partner_id.membership_state == "invoiced"
                    or user.partner_id.membership_state == "free"
                ):
                    already_in_channel = (
                        self.env["slide.channel.partner"]
                        .sudo()
                        .search(
                            [
                                ("partner_id", "=", user.partner_id.id),
                                ("channel_id", "=", record.id),
                            ]
                        )
                    )
                    if not already_in_channel:
                        record._action_add_members(user.partner_id)
        return record

    def write(self, vals):
        record = super(SlideChannel, self).write(vals)
        if vals.get("add_memberships") and vals.get("add_memberships") is True:
            group = (
                self.env["res.groups"].sudo().search([("membership_group", "=", True)])
            )
            for user in group.users:
                if (
                    user.partner_id.membership_state == "paid"
                    or user.partner_id.membership_state == "invoiced"
                    or user.partner_id.membership_state == "free"
                ):
                    already_in_channel = (
                        self.env["slide.channel.partner"]
                        .sudo()
                        .search(
                            [
                                ("partner_id", "=", user.partner_id.id),
                                ("channel_id", "=", record.id),
                            ]
                        )
                    )
                    if not already_in_channel:
                        record._action_add_members(user.partner_id)
        return record
