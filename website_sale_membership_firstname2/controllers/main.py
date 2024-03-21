from odoo import http
from odoo.http import request

class ShowFirstname2(http.Controller):
    @http.route('/show_firstname2', type='json', auth="public", website=True)
    def show_firstname2(self):
        order = request.website.sale_get_order()
        show = False

        if order and order.order_line:
            for line in order.order_line:
                if line.product_id.membership and line.product_id.show_firstname2:
                    show = True
                    break
        return {'show': show}
