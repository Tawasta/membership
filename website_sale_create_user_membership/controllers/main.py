from odoo import http
from odoo.http import request
from odoo.addons.website_sale_create_user.controllers.main import WebsiteSale

class WebsiteSaleMembership(WebsiteSale):
    def handle_new_user(self, order, new_user):
        super(WebsiteSaleMembership, self).handle_new_user(order, new_user)
        
        membership_user = False
        for line in order.order_line:
            if line.product_id.membership:
                membership_user = True
                break

        if membership_user:
            # Käsittele jäsenyyden aktivointi ja siihen liittyvät toimet
            self.assign_membership_group(new_user)
            self.send_membership_email(new_user)

    def assign_membership_group(self, new_user):
        # Etsi jäsenyysryhmä ja lisää uusi käyttäjä ryhmään
        membership_group = request.env['res.groups'].sudo().search([('membership_group', '=', True)], limit=1)
        if membership_group:
            membership_group.sudo().write({'users': [(4, new_user.id)]})

    def send_membership_email(self, new_user):
        # Lähetä jäsenyyteen liittyvä sähköpostiviesti, jos tarpeen
        template = request.env.ref(
            "auth_signup.set_password_email", raise_if_not_found=False
        )
        if template:
            template_values = {
                "email_to": new_user.partner_id.email,
                "email_cc": False,
                "auto_delete": True,
                "partner_to": False,
                "scheduled_date": False,
            }
            attachment_ids = (
                request.env["ir.attachment"]
                .sudo()
                .search([("membership_attachment", "=", True)])
            )
            if attachment_ids:
                template_values.update(
                    {
                        "attachment_ids": [
                            (4, att.id) for att in attachment_ids
                        ],
                    }
                )
            template.sudo().write(template_values)
            template.sudo().send_mail(
                new_user.id, force_send=True, raise_exception=True
            )
