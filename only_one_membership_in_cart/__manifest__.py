##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2021- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################
{
    "name": "Only one membership in cart",
    "version": "17.0.1.0.0",
    "category": "Membership",
    "summary": "Only one membership in cart",
    "website": "https://gitlab.com/tawasta/odoo/membership",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["membership", "product_cant_order"],
    "data": [],
    "assets": {
        "web.assets_frontend": [
            "only_one_membership_in_cart/static/src/js/check_product_in_cart.js",
        ],
        "website.assets_frontend": [
            "only_one_membership_in_cart/static/src/scss/main.scss",
        ]
    },
}
