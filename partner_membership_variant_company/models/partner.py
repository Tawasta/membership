from odoo import api
from odoo import fields
from odoo import models


class MembershipLine(models.Model):

    _inherit = "res.partner"

    member_line_variant_company_ids = fields.Many2many(
        string="Membership companies",
        compute="_compute_member_line_variant_company_ids",
        comodel_name="res.company",
        store=True,
        relation="membership_variant_company_rel",
    )

    @api.depends("member_lines", "member_lines.state")
    def _compute_member_line_variant_company_ids(self):
        print("HERE WE GO")
        print(self)
        for record in self:
            variant_company_ids = record.member_lines.filtered(
                lambda line: line.state in ["waiting", "invoiced", "free", "paid"]
            ).mapped("membership_company_id")
            print(variant_company_ids)

            record.member_line_variant_company_ids = variant_company_ids.ids
