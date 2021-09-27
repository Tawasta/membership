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
        need_contract = False
        needs_double_contract = False
        for li in self.order_line:
            if li.product_id.membership:
                need_contract = True
                if li.product_id.membership_type == "company":
                    needs_double_contract = True

        if need_contract is True:
            if needs_double_contract:
                membership_ids = self._create_memberships(company=True)
            else:
                membership_ids = self._create_memberships()

    def _create_memberships(self, company=False):
        membership_pricelist_id = (
            self.env["product.pricelist"]
            .sudo()
            .search([("membership_pricelist", "=", True)])
        )
        for order in self:
            already_contract = (
                self.env["contract.contract"]
                .sudo()
                .search([("partner_id.email", "=", order.partner_id.email)])
            )

            if company:
                if not order.partner_id.parent_id:
                    order.partner_id.create_company()
                company_contract_vals = {
                    "name": order.partner_id.parent_id.name,
                    "partner_id": order.partner_id.parent_id.id,
                    "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                }
                create_company_contract = (
                    self.env["contract.contract"].sudo().create(company_contract_vals)
                )

                if create_company_contract:
                    contract_line_ids = self._create_contract_lines(
                        create_company_contract, order
                    )

                    contract_vals = {
                        "name": order.partner_id.name,
                        "partner_id": order.partner_id.id,
                        "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                    }
                    create_contract = (
                        self.env["contract.contract"].sudo().create(contract_vals)
                    )
                    if create_contract:
                        contract_line_ids = self._create_contract_lines(
                            create_contract, order, free_products_only=True
                        )

                        current_contract_id = create_company_contract

            else:
                if already_contract:
                    contract_line_ids = self._create_contract_lines(
                        already_contract, order
                    )

                    current_contract_id = already_contract

                else:
                    contract_vals = {
                        "name": self.partner_id.name,
                        "partner_id": self.partner_id.id,
                        "partner_invoice_id": self.partner_invoice_id.id,
                    }
                    create_contract = (
                        self.env["contract.contract"].sudo().create(contract_vals)
                    )
                    if create_contract:
                        contract_line_ids = self._create_contract_lines(
                            create_contract, order
                        )
                        current_contract_id = create_contract

            order.partner_id.sudo().write(
                {"property_product_pricelist": membership_pricelist_id.id}
            )
            order.sudo().write({"contract_id": current_contract_id.id})

    def _create_contract_lines(
        self, contract=False, order=False, free_products_only=False
    ):
        if free_products_only:
            for line in order.order_line:
                if line.product_id.membership:
                    for free_product in line.product_id.free_products_ids:
                        contract_line_vals = {
                            "contract_id": contract.id,
                            "product_id": free_product.id,
                            "name": free_product.name,
                            "price_unit": free_product.lst_price,
                        }
                        create_contract_line = (
                            self.env["contract.line"].sudo().create(contract_line_vals)
                        )
        else:
            for line in order.order_line:
                if line.product_id.membership:
                    contract_line_vals = {
                        "contract_id": contract.id,
                        "product_id": line.product_id.id,
                        "name": line.product_id.name,
                        "price_unit": line.price_unit,
                    }
                    create_contract_line = (
                        self.env["contract.line"].sudo().create(contract_line_vals)
                    )
