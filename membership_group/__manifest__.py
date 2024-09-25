##############################################################################
#
#    Author: Tawasta
#    Copyright 2020 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    "name": "Membership group for active members",
    "summary": "Add active members to a membership group",
    "version": "17.0.1.0.0",
    "category": "Website",
    "website": "https://gitlab.com/tawasta/odoo/membership",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "external_dependencies": {"python": [], "bin": []},
    "depends": [
        "product_pricelist",
        "subscription_oca",
        "website_slides",
    ],
    "data": [
        # "data/ir_cron.xml",
        "views/groups_view.xml",
        # "views/product_pricelist_views.xml",
        "views/slide_channel.xml",
    ],
    "demo": [],
}
