from odoo import models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    def action_confirm(self):
        for record in self:
            if True in record.order_line.mapped("product_id.membership"):
                ir_attachment = self.env["ir.attachment"].sudo()
                attachment_ids = ir_attachment.search(
                    [("membership_attachment", "=", True)]
                )
                for attachment in attachment_ids:
                    new_attachment = attachment.copy()
                    new_attachment.write(
                        {
                            "res_model": record._name,
                            "res_id": record.id,
                            "membership_attachment": False,
                        }
                    )

                record.partner_id.assign_membership_group()

        return super().action_confirm()
