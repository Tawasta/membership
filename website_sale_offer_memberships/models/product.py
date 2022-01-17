##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from odoo import api, fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class ProductPublicCategory(models.Model):
    # 1. Private attributes
    _inherit = "product.public.category"

    # 2. Fields declaration
    is_membership_offer = fields.Boolean(
        "Membership offer",
        default=False,
        help="Offer this category as membership in shopping cart. "
        "Only one category can be selected.",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges
    @api.constrains("is_membership_offer")
    def _is_membership_offer_ensure_one(self):
        if self.is_membership_offer:
            product_public_categories = self.env["product.public.category"].search(
                [("id", "!=", self.id)]
            )
            for product_public_category in product_public_categories:
                product_public_category.is_membership_offer = False

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
