from odoo import api, fields, models


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
        for record in self:
            variant_company_ids = record.member_lines.filtered(
                lambda line: line.state in ["waiting", "invoiced", "free", "paid"]
            ).mapped("membership_company_id")

            record.member_line_variant_company_ids = variant_company_ids.ids

    def cron_compute_member_line_variant_company_ids(self):
        partners = self.search([])
        for record in partners:
            record.with_delay()._compute_member_line_variant_company_ids()
