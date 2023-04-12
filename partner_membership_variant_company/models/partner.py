from datetime import date

from odoo import api, fields, models


class MembershipLine(models.Model):

    _inherit = "res.partner"

    member_line_active_variant_company_ids = fields.Many2many(
        string="Active membership companies",
        compute="_compute_member_line_variant_company_ids",
        comodel_name="res.company",
        store=True,
        relation="membership_active_variant_company_rel",
    )

    member_line_variant_company_ids = fields.Many2many(
        string="All membership companies",
        compute="_compute_member_line_variant_company_ids",
        comodel_name="res.company",
        store=True,
        relation="membership_variant_company_rel",
    )

    @api.depends("member_lines", "member_lines.state")
    def _compute_member_line_variant_company_ids(self):
        for record in self:
            # All membership lines
            membership_lines = record.member_lines.filtered(
                lambda line: line.state in ["waiting", "invoiced", "free", "paid"]
            )

            record.member_line_variant_company_ids = membership_lines.mapped(
                "membership_company_id"
            ).ids

            # Active membership lines only
            active_membership_lines = membership_lines.filtered(
                lambda line: line.date_from
                and line.date_to
                and line.date_from <= date.today() <= line.date_to
            )

            record.member_line_active_variant_company_ids = (
                active_membership_lines.mapped("membership_company_id").ids
            )

    def cron_compute_member_line_variant_company_ids(self):
        partners = self.search([("membership_start", "!=", False)])
        for record in partners:
            record.with_delay()._compute_member_line_variant_company_ids()
