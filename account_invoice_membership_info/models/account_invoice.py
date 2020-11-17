from odoo import api
from odoo import fields
from odoo import models


class AccountInvoice(models.Model):

    _inherit = "account.invoice"

    membership_invoice = fields.Boolean(
        string="Membership invoice",
        compute="_compute_membership_invoice",
        help="Invoice includes membership",
        store=True,
    )

    membership_company_id = fields.Many2one(
        string="Membership for",
        comodel_name="res.company",
        compute="_compute_membership_company",
        store=True,
    )

    membership_line_ids = fields.One2many(
        comodel_name="membership.membership_line",
        compute="_compute_membership_line_ids",
    )

    def _compute_membership_line_ids(self):
        for record in self:
            record.membership_line_ids = record.invoice_line_ids.mapped(
                "membership_line_ids"
            )

    @api.depends("invoice_line_ids")
    def _compute_membership_invoice(self):
        for record in self:
            record.membership_invoice = len(record.membership_line_ids) > 0

    @api.depends("invoice_line_ids")
    def _compute_membership_company(self):
        for record in self:
            company = record.membership_line_ids.mapped("membership_id.company_id")
            if len(company) == 1:
                record.membership_company_id = company.id
