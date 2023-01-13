from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ResGroups(models.Model):

    # 1. Private attributes
    _inherit = "res.groups"

    # 2. Fields declaration
    membership_group = fields.Boolean(
        string="Is a membership group",
        default=False,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.onchange("membership_group")
    def _onchange_membership_group(self):
        if self.membership_group:
            already_selected = (
                self.env["res.groups"].sudo().search([("membership_group", "=", True)])
            )
            if already_selected:
                raise ValidationError(
                    _(
                        "You cannot define that group as a membership "
                        "because another group already has permission."
                    )
                )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
