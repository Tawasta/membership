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
from odoo import fields, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MembershipLine(models.Model):

    # 1. Private attributes
    _inherit = "membership.membership_line"

    # 2. Fields declaration
    membership_company_id = fields.Many2one(
        comodel_name="res.company",
        string="Membership company",
        related="membership_id.variant_company_id",
        store=True,
    )
    contract_state = fields.Selection(
        string="Contract state",
        selection=[
            ("upcoming", "Upcoming"),
            ("in-progress", "In-progress"),
            ("to-renew", "To renew"),
            ("upcoming-close", "Upcoming Close"),
            ("closed", "Closed"),
            ("canceled", "Canceled"),
        ],
        compute="_compute_contract_lines",
        store=True,
    )

    email = fields.Char(string="Partner email", related="partner.email", store=True)

    contract_date_start = fields.Date(related="contract_line_id.date_start")

    invoice_partner_id = fields.Many2one(
        string="Invoice partner",
        comodel_name="res.partner",
        related="account_invoice_id.partner_id",
        store=True,
    )
    membership_product_template_id = fields.Many2one(
        "product.template",
        string="Product Template",
        related="membership_id.product_tmpl_id",
        store=True,
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    def _compute_contract_lines(self):
        for rec in self:
            for invoice in rec.account_invoice_id:
                for invoice_line in invoice.invoice_line_ids:
                    if invoice_line.product_id == rec.membership_id:
                        if invoice_line.contract_line_id.state:
                            rec.contract_state = invoice_line.contract_line_id.state

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
