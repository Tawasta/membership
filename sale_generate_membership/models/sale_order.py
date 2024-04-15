import logging

from dateutil.relativedelta import relativedelta

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    contract_id = fields.Many2one(
        string="Contract", comodel_name="contract.contract", readonly=1, copy=False
    )

    family_members = fields.Many2many(
        string="Family members", comodel_name="res.partner"
    )

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()

        if self.contract_id:
            invoice_vals["old_contract_id"] = self.contract_id.id

        return invoice_vals

    def action_confirm(self):
        response = super(SaleOrder, self).action_confirm()

        membership_line = next(
            (
                line
                for line in self.order_line
                if line.product_id.membership and line.product_id.membership_type
            ),
            None,
        )
        if membership_line:
            self.create_contract(self, membership_line.product_id.membership_type)

        return response

    def create_contract(self, order, membership_type_value):
        if not order.partner_id.email:
            raise UserError(
                _("The sale order customer does not have an email address.")
            )

        if membership_type_value == "contact":
            return self.create_individual_contract(order)
        if membership_type_value == "family":
            return self.create_family_contract(order)

    def create_individual_contract(self, order):
        find_contract_template = (
            self.env["contract.template"].sudo().search([], limit=1)
        )
        contract_vals = {
            "name": order.partner_id.name,
            "partner_id": order.partner_id.id,
            "partner_invoice_id": order.partner_invoice_id.parent_id.id,
            "invoice_partner_id": order.partner_id.id,
            "note": order.note,
            "line_recurrence": True,
            "contract_type": "sale",
            # Lisää muita tarvittavia kenttiä sopimukselle
        }
        contract = self.env["contract.contract"].create(contract_vals)

        contract.sudo().write({"contract_template_id": find_contract_template.id})
        contract._onchange_contract_template_id()

        if contract:
            order.write({"contract_id": contract.id})
            self.create_individual_contract_lines(contract, order)

            # Etsi kaikki liitteet, jotka liittyvät tähän myyntitilaukseen
            find_attachments = self.env["ir.attachment"].search(
                [("res_model", "=", "sale.order"), ("res_id", "=", order.id)]
            )

            # Kopioi liitteet ja päivitä niiden 'res_model' ja 'res_id' vastaamaan sopimusta
            if find_attachments:
                new_attachments = find_attachments.copy(  # noqa: F841
                    {"res_model": "contract.contract", "res_id": contract.id}
                )

        return contract

    def create_individual_contract_lines(self, contract, order):
        if not contract:
            raise ValueError(_("Contract is required to create contract lines."))

        next_year_date = fields.Date.today() + relativedelta(years=1)

        for line in order.order_line.filtered(lambda l: l.product_id.membership):
            price_unit = (
                line.product_id.fix_price
                if line.product_id.product_variant_count > 1
                else line.product_id.lst_price
            )

            contract_line_vals = {
                "contract_id": contract.id,
                "product_id": line.product_id.id,
                "name": line.product_id.name,
                "recurring_rule_type": "yearly",
                "recurring_next_date": next_year_date,
                "price_unit": price_unit,
            }

            contract_line = self.env["contract.line"].create(contract_line_vals)
            line.contract_line_id = contract_line.id

    def create_family_contract(self, order):

        contract = self.create_individual_contract(order)

        if contract:
            for family_member in order.family_members:
                self.send_email_to_family_member(contract, order, family_member)

        return contract

    def send_email_to_family_member(self, contract, order, family_member):

        consent_record = self.env["family.member.consent"].create(
            {
                "family_member_id": family_member.id,
                "user_id": family_member.user_ids
                and family_member.user_ids[0].id
                or False,
                "contract_id": contract.id,
                "order_id": order.id,
            }
        )

        template = self.env.ref("sale_generate_membership.email_template_family_member")
        def_company = self.env["res.company"]._get_main_company()

        template_values = {
            "email_to": family_member.email,
            "email_from": def_company.email,
            "email_cc": False,
            "auto_delete": True,
            "partner_to": False,
            "scheduled_date": False,
        }

        template.sudo().write(template_values)
        template.sudo().send_mail(
            consent_record.id, force_send=True, raise_exception=True
        )

    def create_family_contracts(self, order):
        for family_member in order.family_members:

            consent_record = (
                self.env["family.member.consent"]
                .sudo()
                .search(
                    [
                        ("family_member_id", "=", family_member.id),
                        ("is_used", "=", True),
                        ("order_id", "=", order.id),
                    ],
                    limit=1,
                )
            )

            if consent_record:
                find_contract_template = (
                    self.env["contract.template"].sudo().search([], limit=1)
                )
                family_contract_vals = {
                    "name": family_member.name,
                    "partner_id": family_member.id,
                    "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                    "invoice_partner_id": order.partner_id.id,
                    "note": order.note,
                    "line_recurrence": True,
                    "parent_contract_id": consent_record.contract_id.id,
                    "contract_type": "sale",
                    # Lisää muita tarvittavia kenttiä sopimukselle
                }
                contract = self.env["contract.contract"].create(family_contract_vals)

                consent_record.contract_id.sudo().write(
                    {"parent_contract_id": contract.id}
                )

                contract.sudo().write(
                    {"contract_template_id": find_contract_template.id}
                )
                contract._onchange_contract_template_id()

                if contract:
                    self.create_family_contract_lines(contract, order)

        return contract

    def create_family_contract_lines(self, contract, order):
        if not contract:
            raise ValueError(_("Contract is required to create contract lines."))

        next_year_date = fields.Date.today() + relativedelta(years=1)

        for line in order.order_line.filtered(lambda l: l.product_id.membership):

            for product in line.product_id.extra_products_ids:

                contract_line_vals = {
                    "contract_id": contract.id,
                    "product_id": product.id,
                    "name": product.name,
                    "recurring_rule_type": "yearly",
                    "recurring_next_date": next_year_date,
                    "price_unit": "0",
                }

                contract_line = self.env["contract.line"].create(contract_line_vals)
                line.contract_line_id = contract_line.id

    def action_cancel(self):
        for record in self:
            for line in record.order_line:
                if line.contract_line_id:
                    line.contract_line_id.cancel()

        return super().action_cancel()
