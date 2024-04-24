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
            .search([("membership_pricelist", "=", True)], limit=1)
        )
        # TODO: Handle the situation where multiple pricelists are found
        for order in self:
            company_contract = False
            find_contract_template = self.env["contract.template"].sudo().search([])
            if company:
                if not order.partner_id.parent_id:
                    order.partner_id.create_company()

                if order.contract_id:
                    create_contract = order.contract_id
                else:
                    if find_contract_template:
                        company_contract_vals = (
                            self.env["contract.template"]
                            .sudo()
                            ._prepare_contract_value(find_contract_template)
                        )
                    else:
                        company_contract_vals = {}
                    company_contract_vals.update(
                        {
                            "name": order.partner_id.parent_id.name,
                            "partner_id": order.partner_id.parent_id.id,
                            "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                            "invoice_partner_id": order.partner_id.parent_id.id,
                            "note": order.note,
                            "line_recurrence": True,
                            "date_start": fields.Date.today(),
                        }
                    )
                    create_contract = (
                        self.env["contract.contract"]
                        .sudo()
                        .create(company_contract_vals)
                    )
                    company_contract = create_contract

                if create_contract:
                    self._create_contract_lines(create_contract, order)
                    if find_contract_template:
                        contract_vals = (
                            self.env["contract.template"]
                            .sudo()
                            ._prepare_contract_value(find_contract_template)
                        )
                    else:
                        contract_vals = {}
                    contract_vals.update(
                        {
                            "name": order.partner_id.name,
                            "partner_id": order.partner_id.id,
                            "partner_invoice_id": order.partner_invoice_id.parent_id.id,
                            "invoice_partner_id": order.partner_id.id,
                            "note": order.note,
                            "line_recurrence": True,
                        }
                    )
                    create_contract = (
                        self.env["contract.contract"].sudo().create(contract_vals)
                    )
                    if create_contract:
                        self._create_contract_lines(
                            create_contract, order, free_products_only=True
                        )
                        #create_contract.recurring_create_invoice()

                        related_contract = (
                            self.env["contract.contract"]
                            .sudo()
                            .search(
                                [("partner_id", "=", order.partner_id.parent_id.id)]
                            )
                        )
                        related_contract.sudo().write(
                            {"related_contract_id": create_contract.id}
                        )

            else:
                if order.partner_id.email:
                    already_contract = (
                        self.env["contract.contract"]
                        .sudo()
                        .search([("partner_id.email", "=", order.partner_id.email)])
                    )
                    if already_contract and len(already_contract) == 1:
                        self._create_contract_lines(
                            already_contract,
                            order,
                            free_products_only=False,
                            already_contract=True,
                        )
                        create_contract = already_contract
                    else:
                        if order.contract_id:
                            create_contract = order.contract_id
                        else:
                            if find_contract_template:
                                contract_vals = (
                                    self.env["contract.template"]
                                    .sudo()
                                    ._prepare_contract_value(find_contract_template)
                                )
                            else:
                                contract_vals = {}
                            contract_vals.update(
                                {
                                    "name": self.partner_id.name,
                                    "partner_id": self.partner_id.id,
                                    "partner_invoice_id": self.partner_invoice_id.id,
                                    "invoice_partner_id": self.partner_id.id,
                                    "note": order.note,
                                    "line_recurrence": True,
                                }
                            )
                            create_contract = (
                                self.env["contract.contract"]
                                .sudo()
                                .create(contract_vals)
                            )
                        if create_contract:
                            self._create_contract_lines(create_contract, order)

                else:
                    raise UserError(
                        _(
                            "The sale order customer does not have an email address specified, "
                            "so the membership agreement cannot be created."
                        )
                    )

            order.partner_id.sudo().write(
                {"property_product_pricelist": membership_pricelist_id.id}
            )
            if company_contract:
                order.sudo().write({"contract_id": company_contract.id})
            else:
                order.sudo().write({"contract_id": create_contract.id})

            find_attachments = (
                self.env["ir.attachment"]
                .sudo()
                .search([("res_model", "=", "sale.order"), ("res_id", "=", order.id)])
            )
            for att in find_attachments:
                new_attachment = att.copy()
                new_attachment.sudo().write(
                    {"res_model": "contract.contract", "res_id": create_contract.id}
                )

    # flake8: noqa: C901
    def _create_contract_lines(
        self,
        contract=False,
        order=False,
        free_products_only=False,
        already_contract=False,
    ):
        if free_products_only:
            currentTimeDate = datetime.now().date() + relativedelta(years=1)
            # first_day_of_next_year = currentTimeDate.replace(month=1, day=1)
            for line in order.order_line:
                if line.product_id.membership:
                    if line.product_id.free_products_ids:
                        variant_company_id = line.product_id.variant_company_id
                        for free_p in line.product_id.free_products_ids:
                            for free_l in order.order_line:
                                logging.info(free_l)
                                if (
                                    free_p == free_l.product_id
                                    and free_p.variant_company_id == variant_company_id
                                ):
                                    logging.info(
                                        "====ILMAINEN JOKA ON OSTOSKORISSA====="
                                    )
                                    logging.info(free_p)
                                    contract_line_vals = {
                                        "contract_id": contract.id,
                                        "product_id": free_p.id,
                                        "name": free_p.name,
                                        "recurring_rule_type": "yearly",
                                        "recurring_next_date": currentTimeDate,
                                    }
                                    if free_p.product_variant_count > 1:
                                        contract_line_vals.update(
                                            {"price_unit": free_p.fix_price}
                                        )
                                    else:
                                        contract_line_vals.update(
                                            {"price_unit": free_p.lst_price}
                                        )
                                    contract_line_id = (
                                        self.env["contract.line"]
                                        .sudo()
                                        .create(contract_line_vals)
                                    )
                                    line.contract_line_id = contract_line_id.id
                        variant_product_same_company = (
                            self.env["product.product"]
                            .sudo()
                            .search(
                                [
                                    ("id", "in", line.product_id.free_products_ids.ids),
                                    ("variant_company_id", "=", variant_company_id.id),
                                ]
                            )
                        )
                        logging.info("===SAME VARIANT====")
                        logging.info(variant_product_same_company)
                        if variant_product_same_company:
                            contract_line_vals = {
                                "contract_id": contract.id,
                                "product_id": variant_product_same_company.id,
                                "name": variant_product_same_company.name,
                                "recurring_rule_type": "yearly",
                                "recurring_next_date": currentTimeDate,
                            }
                            if variant_product_same_company.product_variant_count > 1:
                                contract_line_vals.update(
                                    {
                                        "price_unit": variant_product_same_company.fix_price
                                    }
                                )
                            else:
                                contract_line_vals.update(
                                    {
                                        "price_unit": variant_product_same_company.lst_price
                                    }
                                )
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
                            "recurring_rule_type": "yearly",
                            "recurring_next_date": currentTimeDate,
                        }
                        if line.product_id.product_variant_count > 1:
                            contract_line_vals.update(
                                {"price_unit": line.product_id.fix_price}
                            )
                        else:
                            contract_line_vals.update(
                                {"price_unit": line.product_id.lst_price}
                            )
                        contract_line_id = (
                            self.env["contract.line"].sudo().create(contract_line_vals)
                        )
                        line.contract_line_id = contract_line_id.id

        else:
            # ending_day_of_current_year = datetime.now().date().replace(month=12, day=31)
            # first_day_of_next_year = datetime.now().date().replace(year= +1, month=1, day=1)
            currentTimeDate = datetime.now().date() + relativedelta(years=1)
            # first_day_of_next_year = currentTimeDate.replace(month=1, day=1)
            is_company_contract = False
            for li in order.order_line:
                if li.product_id.membership_type == "company":
                    is_company_contract = True

            if is_company_contract:
                for line in order.order_line:
                    if (
                        line.product_id.membership
                        and line.product_id.membership_type == "company"
                    ):
                        contract_line_vals = {
                            "contract_id": contract.id,
                            "product_id": line.product_id.id,
                            "name": line.product_id.name,
                            "recurring_rule_type": "yearly",
                            "recurring_next_date": currentTimeDate,
                        }
                        if already_contract:
                            # all_ended = False
                            ended_lines = []
                            for contract_line in contract.contract_line_fixed_ids:
                                if contract_line.state in (
                                    "closed",
                                    "canceled",
                                    "upcoming-close",
                                ):
                                    ended_lines.append(contract_line)

                            if len(ended_lines) == len(
                                contract.contract_line_fixed_ids
                            ):
                                contract_line_vals.update(
                                    {"price_unit": line.product_id.fix_price}
                                )

                            else:

                                item_price = (
                                    self.env["product.pricelist.item"]
                                    .sudo()
                                    .search(
                                        [
                                            (
                                                "product_tmpl_id",
                                                "=",
                                                line.product_id.product_tmpl_id.id,
                                            ),
                                            ("additional_membership_price", "=", True),
                                        ]
                                    )
                                )
                                contract_line_vals.update(
                                    {"price_unit": item_price.fixed_price}
                                )
                        else:
                            if line.product_id.product_variant_count > 1:
                                contract_line_vals.update(
                                    {"price_unit": line.product_id.fix_price}
                                )
                            else:
                                contract_line_vals.update(
                                    {"price_unit": line.product_id.lst_price}
                                )
                        contract_line_id = (
                            self.env["contract.line"].sudo().create(contract_line_vals)
                        )
                        line.contract_line_id = contract_line_id.id
            else:

                line_counter = 0

                for line in order.order_line:
                    if line.product_id.membership:
                        contract_line_vals = {
                            "contract_id": contract.id,
                            "product_id": line.product_id.id,
                            "name": line.product_id.name,
                            "recurring_rule_type": "yearly",
                            "recurring_next_date": currentTimeDate,
                        }
                        if already_contract:
                            # all_ended = False
                            ended_lines = []
                            for contract_line in contract.contract_line_fixed_ids:
                                if contract_line.state in (
                                    "closed",
                                    "canceled",
                                    "upcoming-close",
                                ):
                                    ended_lines.append(contract_line)

                            if len(ended_lines) == len(
                                contract.contract_line_fixed_ids
                            ):
                                contract_line_vals.update(
                                    {"price_unit": line.product_id.fix_price}
                                )

                            else:
                                item_price = (
                                    self.env["product.pricelist.item"]
                                    .sudo()
                                    .search(
                                        [
                                            (
                                                "product_tmpl_id",
                                                "=",
                                                line.product_id.product_tmpl_id.id,
                                            ),
                                            ("additional_membership_price", "=", True),
                                        ]
                                    )
                                )
                                contract_line_vals.update(
                                    {"price_unit": item_price.fixed_price}
                                )
                        else:
                            if line_counter == 0:
                                if line.product_id.product_variant_count > 1:
                                    contract_line_vals.update(
                                        {"price_unit": line.product_id.fix_price}
                                    )
                                else:
                                    contract_line_vals.update(
                                        {"price_unit": line.product_id.lst_price}
                                    )

                            else:

                                if line.product_id.type != "service":
                                    if line.product_id.product_variant_count > 1:
                                        contract_line_vals.update(
                                            {"price_unit": line.product_id.fix_price}
                                        )
                                    else:
                                        contract_line_vals.update(
                                            {"price_unit": line.product_id.lst_price}
                                        )
                                else:
                                    contract_line_vals.update(
                                        {"price_unit": line.price_unit}
                                    )
                            line_counter += 1

                        contract_line_id = (
                            self.env["contract.line"].sudo().create(contract_line_vals)
                        )
                        line.contract_line_id = contract_line_id.id
