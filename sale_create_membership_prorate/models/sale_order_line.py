from odoo import _, api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.onchange("product_id")
    def product_id_change(self):
        res = super().product_id_change()

        if not self.product_id.membership_contract_prorate:
            return res

        discount, period, period_name = self.order_id._get_contract_prorate_info()

        if discount:
            self.discount = discount
            self.name += _(" ({} {})").format(period, period_name)

        return res
