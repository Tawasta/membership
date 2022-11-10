from odoo import fields
from odoo import models


class SlideChannel(models.Model):
    _inherit = "slide.channel"

    add_memberships = fields.Boolean(string="Add members to this channel", default=False)
