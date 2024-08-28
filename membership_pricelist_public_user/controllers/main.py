from odoo import http
from odoo.http import request
import logging

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSale(WebsiteSale):

    @http.route(['/shop/cart/update_json'], type='json', auth="public", methods=['POST'], website=True, csrf=False)
    def cart_update_json(
        self, product_id, line_id=None, add_qty=None, set_qty=None, display=True,
        product_custom_attribute_values=None, no_variant_attribute_values=None, **kw
    ):
        res = super(WebsiteSale, self).cart_update_json(
            product_id=product_id,
            line_id=line_id,
            add_qty=add_qty,
            set_qty=set_qty,
            display=display,
            product_custom_attribute_values=product_custom_attribute_values,
            no_variant_attribute_values=no_variant_attribute_values,
            **kw
        )

        order = request.website.sale_get_order(force_create=True)
        use_membership_pricelist = False

        # Tarkistetaan, onko käyttäjä julkinen (public user)
        if request.env.user.partner_id.id == request.env.ref("base.public_user").partner_id.id:
            current_line = None

            if add_qty:
                # Käydään läpi ostoskorin rivit
                for line in order.order_line:
                    if line.product_id.subscribable:
                        # Haetaan tuotteen hinta nykyiseltä hinnastolta
                        price_unit = line.order_id.pricelist_id._get_product_price(
                            product=line.product_id,
                            quantity=1.0,
                            currency=order.currency_id,
                            date=order.date_order,
                            **kw,
                        )
                        use_membership_pricelist = True
                        current_line = line

                # Jos käytetään jäsenyyshinnastoa
                if use_membership_pricelist:
                    membership_pricelist = current_line.product_id.pricelist_id

                    # Jos nykyinen hinnasto ei ole jäsenyyshinnasto, vaihdetaan hinnasto
                    if order.pricelist_id != membership_pricelist:
                        request.session['website_sale_current_pl'] = membership_pricelist.id
                        order._cart_update_pricelist(pricelist_id=membership_pricelist.id)

                        # Päivitetään hinnan riville
                        if current_line:
                            current_line.sudo().write({"price_unit": price_unit})
            else:
                # Tarkistetaan, onko tilauksessa vielä subscribable-tuotteita
                has_subscription_product = any(line.product_id.subscribable for line in order.order_line)
            
                if not has_subscription_product:
                    request.session.pop('website_sale_current_pl', None)
                    order._cart_update_pricelist(update_pricelist=True)

        return res
