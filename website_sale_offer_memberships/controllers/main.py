from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):
    def _get_shop_payment_values(self, order, **kwargs):
        render_values = super(WebsiteSale, self)._get_shop_payment_values(
            order, **kwargs
        )
        is_subscribable = False
        for line in order.order_line:
            if line.product_id.subscribable:
                is_subscribable = True
        if order.partner_id.subscription_ids.filtered(lambda s: s.in_progress):
            is_subscribable = True

        if is_subscribable is False:
            membership_categ_id = (
                request.env["product.public.category"]
                .sudo()
                .search([("is_membership_offer", "=", True)])
            )

            if membership_categ_id:
                categ_href = "/shop/category/%s" % membership_categ_id[0].id
            else:
                categ_href = "/shop"
            render_values.update(
                {"show_membership_info": True, "categ_href": categ_href}
            )

        return render_values
