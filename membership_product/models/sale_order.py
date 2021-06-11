from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _create_invoices(self, grouped=False, final=False):
        invoice_ids = super()._create_invoices(grouped=grouped, final=final)
        for invoice in invoice_ids:
            for line in invoice.invoice_line_ids:
                if line.product_id.membership:
                    contract_vals = {
                        "name": invoice.partner_id.name,
                        "partner_id": invoice.partner_id.id,
                    }
                    create_contract = (
                        self.env["contract.contract"].sudo().create(contract_vals)
                    )
                    if create_contract:
                        contract_line_vals = {
                            "contract_id": create_contract.id,
                            "product_id": line.product_id.id,
                            "name": line.product_id.name,
                        }
                        create_contract_line = (
                            self.env["contract.line"].sudo().create(contract_line_vals)
                        )
                        if create_contract_line:
                            invoice.sudo().write(
                                {"old_contract_id": create_contract.id}
                            )

        return invoice_ids
