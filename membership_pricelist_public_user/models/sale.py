from odoo import api
from odoo import fields
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends(
        "qty_delivered_method",
        "qty_delivered_manual",
        "analytic_line_ids.so_line",
        "analytic_line_ids.unit_amount",
        "analytic_line_ids.product_uom_id",
    )
    def _compute_qty_delivered(self):
        res = super()._compute_qty_delivered()
        if self.env.user.id == self.env.ref("base.public_user").id:
            use_membership_pricelist = False
            order_line_list = []
            for line in self.order_id.order_line:
                if line.product_id.membership:
                    order_line_list.append(line)
                    use_membership_pricelist = True
            if use_membership_pricelist:
                order_line = order_line_list[0]

                public_pricelist = self.env.ref("product.list0")
                add_qty = False
                price_unit = public_pricelist.get_product_price(
                    order_line.product_id,
                    add_qty,
                    order_line.order_id.partner_id,
                    uom_id=order_line.product_id.uom_id.id,
                )
                order_line.sudo().write({"price_unit": price_unit})

        return res
