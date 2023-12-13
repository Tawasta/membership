import json
import logging

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website_sale_create_user_membership.controllers.main import (
    WebsiteSaleMembership,
)


class ProductAttributeCheckController(http.Controller):
    @http.route("/check_attribute", type="json", auth="public", website=True)
    def check_attribute(self, selectedAttributeValue=None):
        is_family = False
        if selectedAttributeValue:
            att_id = int(selectedAttributeValue)
            attribute = (
                request.env["product.template.attribute.value"].sudo().browse(att_id)
            )

            if attribute.exists():
                if attribute.attribute_id.family_members_rule:
                    is_family = True

        return {"is_family": is_family}

    @http.route("/get_updated_modal_content", type="json", auth="public", website=True)
    def get_updated_modal_content(self, counterValue=None):
        # Renderöi päivitetty modaalisen ikkunan HTML käyttäen QWebiä
        return request.env["ir.ui.view"]._render_template(
            "website_sale_family_membership.modal_template", {"counter": counterValue}
        )


class WebsiteSale(WebsiteSale):
    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        response = super(WebsiteSale, self).cart_update(
            product_id, add_qty, set_qty, **kw
        )
        family_members_data_json = kw.get("familyMembers", "{}")
        self.create_family_members(family_members_data_json)
        return response

    def create_family_members(self, family_members_data_json):
        # Muutetaan JSON data Python-objektiksi, jotta voidaan käsitellä data
        family_members_data = json.loads(family_members_data_json)

        Partner = request.env["res.partner"].sudo()
        order = request.website.sale_get_order()

        for member_data in family_members_data.values():
            logging.info(member_data)
            new_partner = Partner.create(
                {
                    "firstname": member_data.get("firstname", ""),
                    "lastname": member_data.get("lastname", ""),
                    "email": member_data.get("email", ""),
                }
            )
            order.sudo().write({"family_members": [(4, new_partner.id)]})


class WebsiteSaleFamilyMembers(WebsiteSaleMembership):
    def handle_new_user(self, order, new_user):
        super(WebsiteSaleFamilyMembers, self).handle_new_user(order, new_user)

        # Tarkistetaan, onko tilauksessa family_member-arvoja
        if order.family_members:
            for member in order.family_members:
                self.send_portal_access_email(member)

    def send_portal_access_email(self, member):
        values = {
            "name": member.name,
            "partner_id": member.id,
            "login": member.email,
        }
        member_user = member.user_ids and member.user_ids[0] or False
        res_users = request.env["res.users"].sudo()

        if not member_user:
            member_user = res_users.search([("login", "=", values.get("login"))])

            if not member_user:
                new_user = request.env["res.users"].sudo()._signup_create_user(values)
                if new_user:
                    website = request.env["website"].get_current_website()
                    new_user.sudo().write(
                        {
                            "company_id": website.company_id.id,
                            "company_ids": [(6, 0, website.company_id.ids)],
                        }
                    )
                    new_user.with_context(create_user=True).action_reset_password()
