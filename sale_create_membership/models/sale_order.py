from odoo import fields
from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one(
        string="Contract", comodel_name="contract.contract", readonly=1, copy=False
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()

        if self.contract_id:
            invoice_vals["old_contract_id"] = self.contract_id.id

        return invoice_vals

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
                self._create_memberships(company=True)
            else:
                self._create_memberships()

        return response

    def action_cancel(self):
        for record in self:
            for line in record.order_line:
                if line.contract_line_id:
                    line.contract_line_id.cancel()

        return super().action_cancel()

    def _create_memberships(self, company=False):
        membership_pricelist_id = (
            self.env["product.pricelist"]
            .sudo()
            .search([("membership_pricelist", "=", True)])
        )
        for order in self:
            if company:
                if not order.partner_id.parent_id:
                    order.partner_id.create_company()

                if order.contract_id:
                    create_contract = order.contract_id
                else:
                    company_contract_vals = {
                        "name": order.partner_id.parent_id.name,
                        "partner_id": order.partner_id.parent_id.id,
                        "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                    }
                    create_contract = (
                        self.env["contract.contract"]
                        .sudo()
                        .create(company_contract_vals)
                    )

                if create_contract:
                    self._create_contract_lines(create_contract, order)

                    contract_vals = {
                        "name": order.partner_id.name,
                        "partner_id": order.partner_id.id,
                        "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                    }
                    create_contract = (
                        self.env["contract.contract"].sudo().create(contract_vals)
                    )
                    if create_contract:
                        self._create_contract_lines(
                            create_contract, order, free_products_only=True
                        )

            else:
                already_contract = (
                    self.env["contract.contract"]
                    .sudo()
                    .search([("partner_id.email", "=", order.partner_id.email)])
                )
                if already_contract:
                    self._create_contract_lines(already_contract, order)
                    create_contract = already_contract
                else:
                    if order.contract_id:
                        create_contract = order.contract_id
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
                        self._create_contract_lines(create_contract, order)

            order.partner_id.sudo().write(
                {"property_product_pricelist": membership_pricelist_id.id}
            )
            order.sudo().write({"contract_id": create_contract.id})

    def _create_contract_lines(
        self, contract=False, order=False, free_products_only=False
    ):
        if free_products_only:
            for line in order.order_line:
                if line.product_id.membership:
                    if line.product_id.free_products_ids:
                        variant_company_id = line.product_id.variant_company_id
                        for free_product in line.product_id.free_products_ids:
                            if free_product.variant_company_id == variant_company_id:
                                contract_line_vals = {
                                    "contract_id": contract.id,
                                    "product_id": free_product.id,
                                    "name": free_product.name,
                                    "price_unit": free_product.lst_price,
                                }
                                contract_line_id = (
                                    self.env["contract.line"]
                                    .sudo()
                                    .create(contract_line_vals)
                                )
                                line.contract_line_id = contract_line_id.id
                    if line.product_id.show_only_in_suggested_accessories:
                        contract_line_vals = {
                            "contract_id": contract.id,
                            "product_id": line.product_id.id,
                            "name": line.product_id.name,
                            "price_unit": line.price_unit,
                        }
                        contract_line_id = (
                            self.env["contract.line"].sudo().create(contract_line_vals)
                        )
                        line.contract_line_id = contract_line_id.id

        else:
            for line in order.order_line:
                if (
                    line.product_id.membership
                    and line.product_id.show_only_in_suggested_accessories is False
                ):
                    contract_line_vals = {
                        "contract_id": contract.id,
                        "product_id": line.product_id.id,
                        "name": line.product_id.name,
                        "price_unit": line.price_unit,
                    }
                    contract_line_id = (
                        self.env["contract.line"].sudo().create(contract_line_vals)
                    )
                    line.contract_line_id = contract_line_id.id
