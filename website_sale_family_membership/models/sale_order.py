from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        if self.family_members:
            for member in self.family_members:
                self._create_user_from_order(member)
        return res
