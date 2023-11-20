import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


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

        membership_line = next((line for line in self.order_line if line.product_id.membership and line.product_id.membership_type), None)
        if membership_line:
            self.create_contract(self, membership_line.product_id.membership_type)

        return response



    def create_contract(self, order, membership_type_value):
        if not order.partner_id.email:
            raise UserError("The sale order customer does not have an email address.")

        if membership_type_value == "contact":
            return self.create_individual_contract(order)
        if membership_type_value == "family":
            return self.create_family_contract(order)


    def create_individual_contract(self, order):
        contract_vals = {
            "name": order.partner_id.name,
            "partner_id": order.partner_id.id,
            "partner_invoice_id": order.partner_invoice_id.parent_id.id,
            "invoice_partner_id": order.partner_id.id,
            "note": order.note,
            "line_recurrence": True,
            # Lisää muita tarvittavia kenttiä sopimukselle
        }
        contract = self.env['contract.contract'].create(contract_vals)

        if contract:
            order.write({"contract_id": contract.id})
            self.create_individual_contract_lines(contract, order)

            # Etsi kaikki liitteet, jotka liittyvät tähän myyntitilaukseen
            find_attachments = self.env["ir.attachment"].search([
                ("res_model", "=", "sale.order"), 
                ("res_id", "=", order.id)
            ])

            # Kopioi liitteet ja päivitä niiden 'res_model' ja 'res_id' vastaamaan sopimusta
            find_attachments = self.env["ir.attachment"].search([("res_model", "=", "sale.order"), ("res_id", "=", order.id)])
                if find_attachments:
                    new_attachments = find_attachments.copy({"res_model": "contract.contract", "res_id": contract.id})

        return contract


    def create_individual_contract_lines(self, contract, order):
        if not contract:
            raise ValueError("Contract is required to create contract lines.")

        next_year_date = fields.Date.today() + relativedelta(years=1)
        first_day_of_next_year = next_year_date.replace(month=1, day=1)

        for line in order.order_line.filtered(lambda l: l.product_id.membership):
            price_unit = line.product_id.fix_price if line.product_id.product_variant_count > 1 else line.product_id.lst_price

            contract_line_vals = {
                "contract_id": contract.id,
                "product_id": line.product_id.id,
                "name": line.product_id.name,
                "recurring_rule_type": "yearly",
                "recurring_next_date": first_day_of_next_year,
                "price_unit": price_unit,
            }

            contract_line = self.env["contract.line"].create(contract_line_vals)
            line.contract_line_id = contract_line.id


    def create_family_contract(self, order):
        pass  # Toteuta toiminnallisuus


    def action_cancel(self):
        for record in self:
            for line in record.order_line:
                if line.contract_line_id:
                    line.contract_line_id.cancel()

        return super().action_cancel()

