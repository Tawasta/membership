import json
import logging

from odoo import http
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


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

