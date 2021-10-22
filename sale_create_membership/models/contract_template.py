from odoo import models


class ContractTemplate(models.Model):
    _inherit = "contract.template"

    def _prepare_contract_value(self, contract_template=False):
        if contract_template:
            fields = contract_template._fields.keys()
            vals = self._convert_to_write(contract_template.read(fields)[0])
            vals.pop("id", None)
            vals.pop("create_uid", None)
            vals.pop("create_date", None)
            vals.pop("write_uid", None)
            vals.pop("write_date", None)
            vals.pop("__last_update", None)
        return vals
