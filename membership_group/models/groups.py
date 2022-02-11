##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

# 1. Standard library imports:

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import fields, models, api, _
from odoo.exceptions import Warning

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ResGroups(models.Model):

    # 1. Private attributes
    _inherit = 'res.groups'

    # 2. Fields declaration
    membership_group = fields.Boolean(
        string='Is a membership group',
        default=False,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.onchange("membership_group")
    def _onchange_membership_group(self):
        if self.membership_group:
            allready_selected = (
                self.env["res.groups"]
                .sudo()
                .search([("membership_group", "=", True)])
            )
            if allready_selected:
                raise Warning(
                    _(
                        "You cannot define that group as a membership because another group already has permission."
                    )
                )

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
