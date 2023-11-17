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

        # Oletetaan, että vain yksi tuote per tilaus on merkitty 'membership'-ominaisuudella
        membership_type_value = None

        # Käy läpi tilausrivit
        for line in self.order_line:
            # Tarkista onko tuotteella 'membership' täppä päällä
            if line.product_id.membership and line.product_id.membership_type:
                # Ota 'membership_type' arvo talteen
                membership_type_value = line.product_id.membership_type
                break  # Poistu loopista, kun ensimmäinen tuote löytyy

        # Luo sopimus, jos löytyy 'membership'-tuote
        if membership_type_value:
            self.create_contract(order, membership_type_value)

        return response

    # def create_contract(self, membership_type_value):
    #     if not membership_type_value:
    #         raise ValueError("Membership type value is required to create a contract.")

    #     contract_vals = {
    #         'name': 'Uusi Sopimus {}'.format(self.name),
    #         'partner_id': self.partner_id.id,
    #         'membership_type': membership_type_value,
    #         # Lisää muita tarvittavia kenttiä sopimukselle tässä
    #     }

    #     contract = self.env['contract.contract'].create(contract_vals)
    #     return contract

    def action_cancel(self):
        for record in self:
            for line in record.order_line:
                if line.contract_line_id:
                    line.contract_line_id.cancel()

        return super().action_cancel()

