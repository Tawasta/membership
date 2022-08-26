from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.depends(
        "member_lines.account_invoice_line",
        "member_lines.account_invoice_line.move_id.state",
        "member_lines.account_invoice_line.move_id.payment_state",
        "member_lines.account_invoice_line.move_id.partner_id",
        "free_member",
        "member_lines.date_to",
        "member_lines.date_from",
        "associate_member",
    )
    def _compute_membership_state(self):
        res = super()._compute_membership_state()
        for partner in self:
            if partner.membership_state:
                user = (
                    self.env["res.users"]
                    .sudo()
                    .search([("partner_id", "=", partner.id)])
                )
                group = (
                    self.env["res.groups"]
                    .sudo()
                    .search([("membership_group", "=", True)])
                )
                if user and group:
                    if partner.membership_state in ("paid", "invoiced", "free"):
                        already_in_group = (
                            self.env["res.groups"]
                            .sudo()
                            .search(
                                [
                                    ("id", "=", group.id),
                                    ("users", "in", user.ids),
                                ]
                            )
                        )
                        if not already_in_group:
                            group.sudo().write({"users": [(4, user.id)]})
                        membership_pricelist = (
                            self.env["product.pricelist"]
                            .sudo()
                            .search(
                                [
                                    ("membership_pricelist", "=", True),
                                ]
                            )
                        )
                        user.partner_id.sudo().write(
                            {"property_product_pricelist": membership_pricelist.id}
                        )
                        if user.partner_id.parent_id:
                            user.partner_id.parent_id.sudo().write(
                                {"property_product_pricelist": membership_pricelist.id}
                            )
                    else:
                        group.sudo().write({"users": [(3, user.id)]})

                        public_pricelist = self.env.ref("product.list0")
                        user.partner_id.sudo().write(
                            {"property_product_pricelist": public_pricelist.id}
                        )
                        if user.partner_id.parent_id:
                            user.partner_id.parent_id.sudo().write(
                                {"property_product_pricelist": public_pricelist.id}
                            )
        return res
