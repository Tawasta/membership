import logging
from datetime import datetime, timedelta

from odoo import _, models

_logger = logging.getLogger(__name__)


class ResPartner(models.Model):
    _inherit = "res.partner"


    def _compute_subscription_permissions(self):
        """
        Add or remove subscription permissions
        - group access
        - pricelist based on product's pricelist
        - slide channels
        """
        # Hae liittyvät ryhmät ja kanavat
        group_domain = [("membership_group", "=", True)]
        subscription_groups = self.env["res.groups"].sudo().search(group_domain)

        channels_domain = [("visibility", "=", "members"), ("add_memberships", "=", True)]
        subscription_channels = self.env["slide.channel"].sudo().search(channels_domain)

        for partner in self:
            # Tarkista, onko partnerilla aktiivisia tilauksia
            active_subscriptions = partner.subscription_ids.filtered(
                lambda s: s.stage_id.type == "in_progress"
            )
            user = partner.user_ids and partner.user_ids[0]

            if active_subscriptions:
                # Hae tilaukseen liittyvä tuote ja sen hinnasto
                for subscription in active_subscriptions:
                    product = subscription.sale_subscription_line_ids.mapped('product_id.product_tmpl_id')
                    subscription_pricelist = product.pricelist_id

                    # Lisää käyttäjä tilausryhmiin
                    for group in subscription_groups:
                        if user and user not in group.users:
                            group.sudo().write({"users": [(4, user.id)]})

                    # Aseta tilauksen hinnasto partnerille ja kaupalliselle partnerille
                    if partner.property_product_pricelist != subscription_pricelist:
                        partner.sudo().write({"property_product_pricelist": subscription_pricelist.id})

                    if partner.commercial_partner_id.property_product_pricelist != subscription_pricelist:
                        partner.commercial_partner_id.sudo().write(
                            {"property_product_pricelist": subscription_pricelist.id}
                        )

                    # Lisää partneri tilauskanaviin
                    for channel in subscription_channels:
                        channel._action_add_members(partner)

            else:
                # Jos aktiivisia tilauksia ei ole, poista käyttöoikeudet
                website = self.env['website'].get_current_website()
                public_pricelist = website.pricelist_id

                logging.info("====PUBLIC PRICELIST=====");
                logging.info(public_pricelist);

                # Poista käyttäjä tilausryhmistä
                for group in subscription_groups:
                    if user and user in group.users:
                        group.sudo().write({"users": [(3, user.id)]})

                # Palauta julkinen hinnasto
                if partner.property_product_pricelist != public_pricelist:
                    partner.sudo().write(
                        {"property_product_pricelist": public_pricelist.id}
                    )

                if partner.commercial_partner_id.property_product_pricelist != public_pricelist:
                    partner.commercial_partner_id.sudo().write(
                        {"property_product_pricelist": public_pricelist.id}
                    )

                # Poista partneri tilauskanavista
                for channel in subscription_channels:
                    if channel.visibility == "members" and channel.add_memberships:
                        channel._remove_membership(partner.ids)

