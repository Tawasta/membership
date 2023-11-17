from odoo import http
from odoo.http import request
import logging

class ProductCartCheckController(http.Controller):
    @http.route('/check_product_in_cart', type='json', auth='public', website=True)
    def check_product_in_cart(self, product_id=None):
        in_cart = False
        is_membership_product = False
        order = request.website.sale_get_order()

        if order and product_id:
            product_id = int(product_id)
            product = request.env['product.product'].sudo().browse(product_id)

            is_membership_product = product.membership

            if is_membership_product:
                membership_product_in_cart = any(
                    line.product_id.membership for line in order.order_line
                )
                if membership_product_in_cart:
                    in_cart = True

        logging.info('Product is in cart: %s', in_cart)
        return {'in_cart': in_cart, 'is_membership_product': is_membership_product}
