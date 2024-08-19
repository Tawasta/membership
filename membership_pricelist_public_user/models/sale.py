from odoo import api, models
import logging


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:

            # Tarkistetaan, onko tilauksessa tilauspohjaisia (subscription) tuotteita
            subscription_lines = line.order_id.order_line.filtered(lambda l: l.product_id.subscribable)

            if subscription_lines:
                # Jos tilauksessa on useampi tilauspohjainen tuote
                if len(subscription_lines) > 1:
                    # Ensimmäisen subscription-rivin hintaa ei muuteta
                    first_subscription_line = subscription_lines[0]
                    if line.id == first_subscription_line.id:
                        continue
                # Jos tilauksessa on vain yksi subscription-tuote, ei muuteta sen hintaa
                elif len(subscription_lines) == 1 and subscription_lines[0].id == line.id:
                    continue

            # Jos subscription-tuotteita ei ole tai enemmän kuin yksi, käsitellään muut rivit normaalisti
            super(SaleOrderLine, line)._compute_price_unit()
