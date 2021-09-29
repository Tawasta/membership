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
                    print("=========")
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
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            pricelist_context, pricelist = self._get_pricelist_context()

            print(pricelist)
            for line in order.order_line:
                if line.product_id.membership:
                    use_membership_pricelist = True
                    current_line = line

            if use_membership_pricelist:
                membership_pricelist = (
                    request.env["product.pricelist"]
                    .sudo()
                    .search(
                        [
                            ("membership_pricelist", "=", True),
                            ("name", "ilike", "jäsen"),
                        ]
                    )
                )

                if not order.pricelist_id.membership_pricelist:
                    request.website.sale_get_order(
                        force_pricelist=membership_pricelist.id
                    )
                    # public_pricelist = order.partner_id.property_product_pricelist
                    public_items = (
                        request.env["product.pricelist.item"]
                        .sudo()
                        .search(
                            [
                                ("pricelist_id", "=", pricelist.id),
                                ("product_id", "=", current_line.product_id.id),
                            ]
                        )
                    )
                    if public_items:
                        find_date_item = False
                        date = datetime.now()
                        for item in public_items:
                            if item.date_start and item.date_end:
                                if item.date_start <= date <= item.date_end:
                                    find_date_item = True
                                    current_line.sudo().write(
                                        {"price_unit": item.fixed_price}
                                    )
                        if find_date_item is False:
                            for item in public_items:
                                if not item.date_start and not item.date_end:
                                    current_line.sudo().write(
                                        {"price_unit": item.fixed_price}
                                    )
                    else:
                        current_line.sudo().write(
                            {"price_unit": current_line.product_id.lst_price}
                        )

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
            order.partner_id.id == request.website.user_id.sudo().partner_id.id
            and order.pricelist_id.membership_pricelist
        ):
            order_line_list = []
            for line in order.order_line:
                if line.product_id.membership:
                    order_line_list.append(line)
                    use_membership_pricelist = True

            if use_membership_pricelist is False:
                request.website.sale_get_order(
                    force_pricelist=request.env["product.pricelist"]
                    .search([("name", "=", "Public Pricelist")])
                    .id
                )

            if use_membership_pricelist:
                order_line = order_line_list[0]

                public_pricelist = order.partner_id.property_product_pricelist

                public_items = (
                    request.env["product.pricelist.item"]
                    .sudo()
                    .search(
                        [
                            ("pricelist_id", "=", public_pricelist.id),
                            ("product_id", "=", order_line.product_id.id),
                        ]
                    )
                )
                if public_items:
                    find_date_item = False
                    date = datetime.now()
                    for item in public_items:
                        if item.date_start and item.date_end:
                            if item.date_start <= date <= item.date_end:
                                find_date_item = True
                                if order_line.price_unit != item.fixed_price:
                                    order_line.sudo().write(
                                        {"price_unit": item.fixed_price}
                                    )

                    if find_date_item is False:
                        for item in public_items:
                            if not item.date_start and not item.date_end:
                                if order_line.price_unit != item.fixed_price:
                                    order_line.sudo().write(
                                        {"price_unit": item.fixed_price}
                                    )
                else:
                    if order_line.price_unit != order_line.product_id.lst_price:
                        order_line.sudo().write(
                            {"price_unit": order_line.product_id.lst_price}
                        )

                return request.redirect("/shop/cart")

        return value
