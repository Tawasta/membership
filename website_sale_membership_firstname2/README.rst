.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
website_sale_membership_firstname2
==================================
* This Odoo module enhances the website sale form by conditionally showing a second firstname field (firstname2) for specific products. It introduces a Boolean field show_firstname2 on product templates, which determines whether firstname2 should be displayed on the website sale form. A JSON controller /show_firstname2 checks if any product in the cart requires the firstname2 field to be shown. Based on this, a JavaScript widget toggles the visibility of the firstname2 field on the form. This feature allows for greater customization and flexibility in capturing customer information for membership or subscription-based products.

Configuration
=============
\-

Usage
=====
\-

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
