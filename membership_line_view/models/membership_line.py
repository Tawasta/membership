from odoo import models, fields
from odoo.addons.membership.models.membership import STATE


class MembershipLine(models.Model):

    # 1. Private attributes
    _inherit = "membership.membership_line"

    # 2. Fields declaration
    membership_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Membership company',
        related='membership_id.company_id',
        store=True,
    )

    override_state = fields.Selection(
        STATE,
        string="Overridden status",
        help="Setting this will override the automated state from invoice"
    )

    contract_state = fields.Selection(
        string="Contract state",
        selection=[
            ('upcoming', 'Upcoming'),
            ('in-progress', 'In-progress'),
            ('to-renew', 'To renew'),
            ('upcoming-close', 'Upcoming Close'),
            ('closed', 'Closed'),
            ('canceled', 'Canceled'),
        ],
        compute="_compute_contract_lines",
        store=True,
    )

    def _compute_state(self):
        for line in self:
            if line.override_state:
                line.state = line.override_state
            else:
                super(MembershipLine, line)._compute_state()

    def action_override_state(self):
        self.ensure_one()
        context = {
            "default_membership_line_id": self.id,
        }
        context.update(self.env.context)
        view_id = self.env.ref(
            "membership_line_view.membership_line_wizard_update_form"
        ).id
        return {
            "type": "ir.actions.act_window",
            "name": "Update membership state",
            "res_model": "membership.line.wizard",
            "view_mode": "form",
            "views": [(view_id, "form")],
            "target": "new",
            "context": context,
        }

    def action_compute_state(self):
        self._compute_state()

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
