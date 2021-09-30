from odoo import fields
from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    contract_line_id = fields.Many2one(
        string="Contract line", comodel_name="contract.line", readonly=1, copy=False
    )

    def _prepare_invoice_line(self, **optional_values):
        res = super()._prepare_invoice_line(**optional_values)

        contract = self.order_id.contract_id
        if contract:
            contract_line = contract.contract_line_fixed_ids.filtered(
                lambda r: r.product_id == self.product_id
            )
            if contract_line:
                res["contract_line_id"] = contract_line.id

        return res
