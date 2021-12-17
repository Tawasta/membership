##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2020- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
    "name": "Mass Mailing List membership line",
    "summary": "Create mass mailing list from membership.membership_line view.",
    "category": "Membership",
    "version": "14.0.1.0.0",
    "website": "",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["mass_mailing", "mass_mailing_partner", "membership_line_view"],
    "data": ["security/ir.model.access.csv","wizard/membership_line_mail_list_wizard.xml"],
    "qweb": [],
}
