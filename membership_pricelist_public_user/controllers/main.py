from odoo import http
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request


class WebsiteSale(WebsiteSale):
    @http.route()
    def cart_update(self, product_id, add_qty=1, set_qty=0, **kw):
        res = super(WebsiteSale, self).cart_update(product_id, add_qty, set_qty)
        order = request.website.sale_get_order(force_create=True)
        use_membership_pricelist = False
        if order.partner_id.id == request.website.user_id.sudo().partner_id.id:
            for line in order.order_line:
                if line.product_id.membership:
                    use_membership_pricelist = True
                    current_product = line.product_id

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
                    new_name = order.name + "_" + "pricelist"
                    new_membership_pricelist = membership_pricelist.copy(
                        {"name": new_name}
                    )
                    for item in new_membership_pricelist.item_ids:
                        if item.product_tmpl_id == current_product.product_tmpl_id:
                            item.unlink()

                    request.website.sale_get_order(
                        force_pricelist=new_membership_pricelist.id
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
            products = []
            for line in order.order_line:
                if line.product_id.membership:
                    products.append(line.product_id)
                    use_membership_pricelist = True

            if use_membership_pricelist is False:
                if order.pricelist_id.name.startswith(str(order.name)):
                    pricelist_archived = order.pricelist_id
                request.website.sale_get_order(
                    force_pricelist=request.env["product.pricelist"]
                    .search([("name", "=", "Public Pricelist")])
                    .id
                )
                pricelist_archived.sudo().write({"active": False})
            if use_membership_pricelist:
                product = products[0]
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
                new_name = order.name + "_" + "pricelist"
                new_membership_pricelist = membership_pricelist.copy({"name": new_name})
                for item in new_membership_pricelist.item_ids:
                    if item.product_tmpl_id == product.product_tmpl_id:
                        item.unlink()
                pricelist_archived = order.pricelist_id
                request.website.sale_get_order(
                    force_pricelist=new_membership_pricelist.id
                )
                pricelist_archived.sudo().write({"active": False})

                return request.redirect("/shop/cart")

        return value
