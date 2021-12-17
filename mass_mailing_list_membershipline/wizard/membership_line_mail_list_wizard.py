from odoo import _, api, fields, models
from odoo.exceptions import UserError


class MembershipLineMailListWizard(models.TransientModel):
    _name = "membership.membership_line.mail.list.wizard"
    _description = "Create contact mailing list"

    mail_list_id = fields.Many2one(
        comodel_name="mailing.list", string="Mailing List"
    )
    membership_line_ids = fields.Many2many(
        comodel_name="membership.membership_line",
        relation="mail_list_wizard_line",
        default=lambda self: self.env.context.get("active_ids"),
    )

    def add_to_mail_list_line(self):
        contact_obj = self.env["mailing.contact"]
        membershiplines = self.membership_line_ids
        # current_students = students.mapped('student_id')
        partners = membershiplines.mapped('partner')
        user_data = []
        mail_list_contacts = self.mail_list_id.contact_ids.mapped("partner_id")

        for partner in partners:
            if partner.id not in mail_list_contacts.ids:
                if partner.email not in user_data:
                    if partner.email:
                        contact_vals = {
                            "partner_id": partner.id,
                            "list_ids": [[6, 0, [self.mail_list_id.id]]],
                            "title_id": partner.title or False,
                            "company_name": partner.company_id.name or False,
                            "country_id": partner.country_id or False,
                            "tag_ids": partner.category_id or False,
                        }
                        contact_obj.create(contact_vals)
                        user_data.append(partner.email)
