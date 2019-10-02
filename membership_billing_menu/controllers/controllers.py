# -*- coding: utf-8 -*-
from odoo import http

# class MembershipBillingMenu(http.Controller):
#     @http.route('/membership_billing_menu/membership_billing_menu/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/membership_billing_menu/membership_billing_menu/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('membership_billing_menu.listing', {
#             'root': '/membership_billing_menu/membership_billing_menu',
#             'objects': http.request.env['membership_billing_menu.membership_billing_menu'].search([]),
#         })

#     @http.route('/membership_billing_menu/membership_billing_menu/objects/<model("membership_billing_menu.membership_billing_menu"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('membership_billing_menu.object', {
#             'object': obj
#         })