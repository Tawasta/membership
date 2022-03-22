from odoo import fields
from odoo import models
from odoo import _
from odoo.exceptions import ValidationError


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
                lambda r: r.state not in ("closed", "canceled", "upcoming-close")
                and r.product_id == self.product_id
            )
            if len(contract_line) > 1:
                raise ValidationError(
                    _(
                        "Contract '{}' has multiple lines for '{}'. Please close redundant contract lines.".format(
                            contract.display_name, self.product_id.display_name
                        )
                    )
                )

            if contract_line:
                res["contract_line_id"] = contract_line.id
            for line in contract_line:
                line._update_recurring_next_date()
        return res
