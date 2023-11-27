from odoo import api, fields, models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    note = fields.Html("Terms and conditions")

    parent_contract_id = fields.Many2one(string="Parent contract", comodel_name="contract.contract")

    @api.model
    def _set_start_contract_modification(self):
        contract = super()._set_start_contract_modification()
        subtype_id = self.env.ref("mail.mt_comment")
        if subtype_id and self.message_follower_ids:
            for follower in self.message_follower_ids:
                if follower.partner_id == self.partner_id:
                    follower.sudo().write({"subtype_ids": [[6, 0, [subtype_id[0].id]]]})
        return contract
