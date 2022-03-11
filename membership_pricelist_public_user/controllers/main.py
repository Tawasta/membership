from datetime import datetime

from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):
    def _checkout_form_save(self, mode, checkout, all_values):
        order = request.website.sale_get_order(force_create=True)
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            if order.pricelist_id.membership_pricelist:

                if mode[0] == "new":
                    checkout.update(
                        {"property_product_pricelist": order.pricelist_id.id}
                    )
        res = super(WebsiteSale, self)._checkout_form_save(mode, checkout, all_values)

        return res

    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        res = super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)
        order = request.website.sale_get_order(force_create=True)
        use_membership_pricelist = False
        if request.env.user.partner_id.id == request.env.ref('base.public_user').partner_id.id

            for line in order.order_line:
                if line.product_id.membership:
                    price_unit = line.order_id.pricelist_id.get_product_price(
                        line.product_id,
                        add_qty,
                        line.order_id.partner_id,
                        uom_id=line.product_id.uom_id.id,
                    )
                    use_membership_pricelist = True
                    current_line = line

            if use_membership_pricelist:
                membership_pricelist = (
                    request.env["product.pricelist"]
                    .sudo()
                    .search([("membership_pricelist", "=", True),])
                )

                if not order.pricelist_id.membership_pricelist:
                    request.website.sale_get_order(
                        force_pricelist=membership_pricelist.id
                    )

                    current_line.sudo().write({"price_unit": price_unit})

            return res

        else:
            return res

    @http.route()
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True
    ):
        value = super(WebsiteSale, self).cart_update_json(
            product_id, line_id, add_qty, set_qty, display
        )
        order = request.website.sale_get_order(force_create=True)
        use_membership_pricelist = False
        if (
            request.env.user.partner_id.id == request.env.ref('base.public_user').partner_id.id
            and order.pricelist_id.membership_pricelist
        ):
            order_line_list = []
            for line in order.order_line:
                if line.product_id.membership:
                    order_line_list.append(line)
                    use_membership_pricelist = True

            if use_membership_pricelist is False:
                request.website.sale_get_order(
                    force_pricelist=request.env.ref("product.list0").id
                )

            if use_membership_pricelist:
                order_line = order_line_list[0]

                public_pricelist = request.env.ref("product.list0")

                price_unit = public_pricelist.get_product_price(
                    order_line.product_id,
                    add_qty,
                    order_line.order_id.partner_id,
                    uom_id=order_line.product_id.uom_id.id,
                )

                order_line.sudo().write({"price_unit": price_unit})

                return request.redirect("/shop/cart")

        return value
