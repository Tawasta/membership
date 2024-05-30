import logging
import math

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _calculate_last_date_invoiced(self):
        last_date_invoiced = self._get_existing_membership_last_date_invoiced()
        if last_date_invoiced:
            res = last_date_invoiced
        else:
            res = super()._calculate_last_date_invoiced()

        return res

    def _get_existing_membership_contract_line(self):
        self.ensure_one()

        # Get the next invoiceable membership line from contracts
        contract_line = (
            self.env["contract.line"]
            .sudo()
            .search(
                [
                    ("contract_id.partner_id", "=", self.partner_id.id),
                    ("product_id.membership", "=", True),
                ],
                order="recurring_next_date",
                limit=1,
            )
        )

        return contract_line

    def _get_existing_membership_last_date_invoiced(self):
        self.ensure_one()

        existing_contract_line = self._get_existing_membership_contract_line()
        last_date = existing_contract_line.last_date_invoiced

        return last_date

    def _get_contract_prorate_info(self):
        self.ensure_one()

        last_date = self._get_existing_membership_last_date_invoiced()
        days_difference = last_date - fields.Date().today()
        discount = 0

        # TODO: configurable method (days, month)
        prorate_method = "month"
        # TODO: configurable rounding (floor, round, ceil)
        prorate_rounding = "ceil"

        if prorate_method == "month":
            period_name = _("months")
            period = days_difference.days / 30
            if prorate_rounding == "ceil":
                period = math.ceil(period)
            discount = 100 / 12 * period
            if discount < 0:
                # If the next invoice date is in the past, we'll get a negative discount
                discount = 0

        return discount, period, period_name
