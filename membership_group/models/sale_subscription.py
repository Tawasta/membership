from odoo import api, fields, models, _
from datetime import date

class SaleSubscription(models.Model):
    _inherit = "sale.subscription"

    def action_start_subscription(self):
        result = super(SaleSubscription, self).action_start_subscription()
        # Kun tilaus alkaa, päivitetään partnerin oikeudet
        for subscription in self:
            subscription.partner_id._compute_subscription_permissions()

        return result

    def action_close_subscription(self):
        """
        Päätä tilaus ja säilytä core-logiikka, mutta lisää myös kumppanin oikeuksien päivitys.
        """
        # Säilytetään core-logiikka kutsumalla super-metodia
        result = super(SaleSubscription, self).action_close_subscription()

        # Päivitetään kumppanin (partner) oikeudet tilauksen sulkemisen jälkeen
        for subscription in self:
            if subscription.partner_id:
                subscription.partner_id._compute_subscription_permissions()

        return result

    def write(self, values):
        res = super(SaleSubscription, self).write(values)
        # Jos tilauksen tila muuttuu (in_progress tai post), päivitä partnerin oikeudet
        if "stage_id" in values:
            for subscription in self:
                subscription.partner_id._compute_subscription_permissions()
        return res