from odoo import models, fields, api, _
import uuid

class FamilyMemberConsent(models.Model):
    _name = 'family.member.consent'
    _description = 'Family Member Consent'
    _sql_constraints = [
        (
            "code_unique",
            "unique(code)",
            _("Code has to be unique for every invite!"),
        )
    ]


    family_member_id = fields.Many2one('res.partner', string='Family Member')
    user_id = fields.Many2one(
        comodel_name="res.users",
        string="Used by",
        help="User who accepted the invitation",
    )
    contract_id = fields.Many2one('contract.contract', string='Contract')
    order_id = fields.Many2one('sale.order', string='Order')
    code = fields.Char(string='Unique Code', readonly=True, copy=False, index=True, default=lambda self: uuid.uuid4().hex)
    is_used = fields.Boolean(string='Is Used', default=False)

    company_id = fields.Many2one(
        comodel_name="res.company",
        default=lambda self: self.env.company,
    )