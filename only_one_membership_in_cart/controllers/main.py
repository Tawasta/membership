from odoo import http
from odoo.http import request


class ProductCartCheckController(http.Controller):
    @http.route("/check_product_in_cart", type="json", auth="public", website=True)
    def check_product_in_cart(self, product_id=None):
        in_cart = False
        is_membership_product = False
        order = request.website.sale_get_order()

        if order and product_id:
            product_id = int(product_id)
            product = request.env["product.product"].sudo().browse(product_id)

            # Tarkista, onko tuote jäsenyystuote
            is_membership_product = product.membership

            # Tarkista jokainen tuote korissa
            for line in order.order_line:
                # Jos tuote on jäsenyystuote ja korissa on muita jäsenyystuotteita
                if (
                    is_membership_product
                    and line.product_id.membership
                    and line.product_id.product_tmpl_id.id != product.product_tmpl_id.id
                ):
                    in_cart = True
                    break
                # Jos sama tuote-ID löytyy jo korista
                elif line.product_id.id == product.id:
                    in_cart = True
                    break
                # Jos kyseessä on sama tuoteperhe (template), mutta eri tuotevariantti
                elif (
                    line.product_id.product_tmpl_id.id == product.product_tmpl_id.id
                    and line.product_id.id != product_id
                ):
                    in_cart = False
                    break

        return {"in_cart": in_cart, "is_membership_product": is_membership_product}
