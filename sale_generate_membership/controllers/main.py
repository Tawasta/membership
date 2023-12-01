from odoo import http
from odoo.http import request
from werkzeug import exceptions

class ConsentController(http.Controller):

    @http.route('/contract/invite/code/<string:code>', type='http', auth='user', website=True)
    def contract_invite(self, code, **kwargs):
        consent_record = request.env['family.member.consent'].sudo().search([('code', '=', code)], limit=1)

        # Tarkista, onko nykyinen käyttäjä sama kuin consent_recordin käyttäjä
        if consent_record and consent_record.user_id and consent_record.user_id != request.env.user:
            raise exceptions.Forbidden()

        if not consent_record or consent_record.is_used:
            raise exceptions.Forbidden()

        values = {
            'consent_record': consent_record,
        }

        return request.render('sale_generate_membership.contract_invite_consent', values)


    @http.route('/contract/consent/accept/<string:code>', type='http', auth='user', methods=['POST'], website=True)
    def accept_consent(self, code, **kwargs):
        consent_record = request.env['family.member.consent'].sudo().search([('code', '=', code)], limit=1)

        # Tarkista, onko nykyinen käyttäjä sama kuin consent_recordin käyttäjä
        if consent_record and consent_record.user_id and consent_record.user_id != request.env.user:
            raise exceptions.Forbidden()

        if not consent_record or consent_record.is_used:
            raise exceptions.Forbidden()

        order = consent_record.order_id
        if not order:
            raise exceptions.Forbidden()

        order_model = request.env[order._name].sudo()
        order_model.create_family_contracts(order)

        consent_record.write({'is_used': True})

        return request.render('sale_generate_membership.contract_consent_success')

