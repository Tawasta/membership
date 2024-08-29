from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def create_subscription(self, lines, subscription_tmpl):
        results = super(SaleOrder, self).create_subscription(lines, subscription_tmpl)

        # Etsitään subscription-objekti
        subscription = self.subscription_ids and self.subscription_ids[0] or False

        if not subscription:
            return results

        for line in self.order_line:
            if line.product_id.membership_type == "company":
                # Luodaan subscription-rivi yritykselle
                company_line_vals = self._prepare_company_subscription_line(line, subscription)
                self.env["sale.subscription.line"].create(company_line_vals)

        # Palautetaan tulos
        return results


    def _prepare_company_subscription_line(self, line, subscription):
        """ Valmistellaan yrityksen subscription-rivi """

        # Tarkistetaan, onko ilmaisia tuotteita ja sama varianttiyhtiö
        correct_product = False
        if line.product_id.free_product_id:
            free_product = next((
                free_p for free_p in line.product_id.free_products_id.product_variant_ids
                if free_p.variant_company_id == line.product_id.variant_company_id
            ), None)

            # Jos ilmainen tuote löytyi, käytetään sitä
            if free_product:
                correct_product = free_product


        # Haetaan tuotteen verot ja mahdolliset alennukset core-logiikan mukaisesti
        fpos = subscription.fiscal_position_id or subscription.partner_id.property_account_position_id
        taxes = correct_product.taxes_id.filtered(lambda tax: tax.company_id == subscription.company_id)
        taxes = fpos.map_tax(taxes) if fpos else taxes

        return {
            'sale_subscription_id': subscription.id,
            'product_id': correct_product.id,
            'name': correct_product.name,
            'price_unit': correct_product.lst_price,
            'product_uom_qty': 1.0,
            'tax_ids': [(6, 0, taxes.ids)],
            'currency_id': subscription.currency_id.id,
            'partner_id': subscription.sale_order_id.partner_id.parent_id.id,
        }

