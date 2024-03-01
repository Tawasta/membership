from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    extra_products_ids = fields.Many2many(
        "product.product",
        string="Extra products",
    )

    membership_type = fields.Selection(
        [("family", "Family"), ("contact", "Contact"), ("company", "Company")],
        string="Membership Type",
        default="contact",
        required=True,
    )

    # Enable setting custom consent texts
    custom_consent_text_initial_msg = fields.Html(
        string="Custom Consent Text: Initial Message",
        translate=True,
        help="Text shown to the user as they first reach the consent page, "
        "e.g. 'You have been invited to accept a contract.'",
    )

    custom_consent_text_popup_msg = fields.Html(
        string="Custom Consent Text: Popup Dialog Message",
        translate=True,
        help="Text shown to the user as they are about top confirm the consent in the  "
        "pop up, e.g. 'You are about to give your consent. Are you sure?'",
    )

    custom_consent_text_confirmation_msg = fields.Html(
        string="Custom Consent Text: Post-confirmation Message",
        translate=True,
        help="Text shown to the user after they have given the consent, e.g. "
        "'Your consent for the contract creation has been successfully registered.'",
    )
