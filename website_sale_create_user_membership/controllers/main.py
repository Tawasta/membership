from odoo.http import request
from odoo import http

from odoo.addons.website_sale_create_user.controllers.main import WebsiteSale


class WebsiteSaleMembership(WebsiteSale):

    @http.route()
    def payment_confirmation(self, **post):
        create_user_always = request.env['ir.config_parameter'].sudo().get_param('website_sale_create_user.always_create_user', default='False')
        sale_order_id = request.session.get("sale_last_order_id")
        if sale_order_id:
            order = request.env["sale.order"].sudo().browse(sale_order_id)
            membership_product_exists = any(line.product_id.membership for line in order.order_line)

            if create_user_always == 'True' or membership_product_exists:
                self.create_user_from_order(order)

        return super(WebsiteSaleMembership, self).payment_confirmation(**post)

    def handle_new_user(self, order, new_user):
        template_values = super(WebsiteSaleMembership, self).handle_new_user(
            order, new_user
        )

        membership_user = False
        for line in order.order_line:
            if line.product_id.membership:
                membership_user = True
                break

        if membership_user:

            attachment_ids = (
                request.env["ir.attachment"]
                .sudo()
                .search([("membership_attachment", "=", True)])
            )
            if attachment_ids:
                template_values.update(
                    {
                        "attachment_ids": [(4, att.id) for att in attachment_ids],
                    }
                )
            self.assign_membership_group(new_user)

        return template_values

    def assign_membership_group(self, new_user):
        # Etsi jäsenyysryhmä ja lisää uusi käyttäjä ryhmään
        membership_group = (
            request.env["res.groups"]
            .sudo()
            .search([("membership_group", "=", True)], limit=1)
        )
        if membership_group:
            membership_group.sudo().write({"users": [(4, new_user.id)]})
