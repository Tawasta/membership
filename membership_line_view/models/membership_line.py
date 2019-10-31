from odoo import models, fields


class MembershipLine(models.Model):
    _inherit = 'membership.membership_line'

    membership_company_id = fields.Many2one(
        comodel_name='res.company',
        string='Membership company',
        related='membership_id.company_id',
        store=True,
    )
