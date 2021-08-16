from odoo import fields
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one(string="Contract", comodel_name="contract.contract")

    def _create_invoices(self, grouped=False, final=False):
        invoice_ids = super()._create_invoices(grouped=grouped, final=final)
        for invoice in invoice_ids:
            contract_so = (
                self.env["sale.order"]
                .sudo()
                .search([("invoice_ids", "in", invoice.ids)])
            )
            if contract_so:
                invoice.sudo().write({"old_contract_id": contract_so.contract_id.id})

        return invoice_ids

    def action_confirm(self):
        response = super(SaleOrder, self).action_confirm()
        contract_vals = {
            "name": self.partner_id.name,
            "partner_id": self.partner_id.id,
        }
        create_contract = self.env["contract.contract"].sudo().create(contract_vals)
        if create_contract:
            for line in self.order_line:
                if line.product_id.membership:
                    contract_line_vals = {
                        "contract_id": create_contract.id,
                        "product_id": line.product_id.id,
                        "name": line.product_id.name,
                    }
                    create_contract_line = (
                        self.env["contract.line"].sudo().create(contract_line_vals)
                    )
            self.sudo().write({"contract_id": create_contract.id})

            membership_pricelist_id = (
                self.env["product.pricelist"]
                .sudo()
                .search([("membership_pricelist", "=", True)])
            )
            self.partner_id.sudo().write(
                {"property_product_pricelist": membership_pricelist_id.id}
            )
