import logging
from datetime import datetime, timedelta

from odoo import _, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"

    def write(self, vals):
        # Override to trigger permissions change when membership state changes
        if "membership_state" in vals or "free_member" in vals:
            msg = _("Compute membership permissions for {}".format(self.ids))
            self.with_delay(description=msg)._compute_membership_permissions()

        return super().write(vals)

    def cron_compute_membership_permissions(self):
        """
        Compute partner membership permissions
        """
        # We'll need to go through all partners to ensure we add and remove all
        # necessary permissions
        timespan = datetime.now() - timedelta(weeks=2)
        partners = self.search([("write_date", ">", timespan)])
        for partner in partners:
            msg = _("Compute membership permissions for {}".format(partner.name))
            partner.with_delay(description=msg)._compute_membership_permissions()

    def _compute_membership_permissions(self):
        """
        Add or remove membership permissions
        - group access
        - pricelist
        - slide channels
        """

        group_domain = [("membership_group", "=", True)]
        membership_groups = self.env["res.groups"].sudo().search(group_domain)

        pricelist_domain = [("membership_pricelist", "=", True)]
        membership_pricelist = (
            self.env["product.pricelist"].sudo().search(pricelist_domain, limit=1)
        )

        channels_domain = [
            ("visibility", "=", "members"),
            ("add_memberships", "=", True),
        ]
        membership_channels = self.env["slide.channel"].sudo().search(channels_domain)

        for partner in self:
            is_member = partner.membership_state in ["paid", "invoiced", "free"]
            user = partner.user_ids and partner.user_ids[0]

            if is_member:
                # Add user to membership groups
                for group in membership_groups:
                    if user and user in group.users:
                        # Nothing to do
                        continue
                    elif user:
                        group.sudo().write({"users": [(4, user.id)]})
                # Add membership pricelist for partner and commercial partner
                if partner.property_product_pricelist != membership_pricelist:
                    partner.sudo().write(
                        {"property_product_pricelist": membership_pricelist.id}
                    )

                if (
                    partner.commercial_partner_id.property_product_pricelist
                    != membership_pricelist
                ):
                    partner.commercial_partner_id.sudo().write(
                        {"property_product_pricelist": membership_pricelist.id}
                    )

                # Add to membership channels
                for channel in membership_channels:
                    channel._action_add_members(partner)

            else:
                # TODO: configurable default pricelist
                public_pricelist = self.env.ref("product.list0")
                # Remove user from membership groups
                for group in membership_groups:
                    if user and user in group.users:
                        group.sudo().write({"users": [(3, user.id)]})
                # Remove membership pricelist
                if partner.property_product_pricelist != public_pricelist:
                    partner.sudo().write(
                        {"property_product_pricelist": public_pricelist.id}
                    )

                if (
                    partner.commercial_partner_id.property_product_pricelist
                    != public_pricelist
                ):
                    partner.commercial_partner_id.sudo().write(
                        {"property_product_pricelist": public_pricelist.id}
                    )
                # Remove from membership channels
                for channel in membership_channels:
                    if channel.visibility == "members" and channel.add_memberships:
                        channel._remove_membership(partner.ids)
