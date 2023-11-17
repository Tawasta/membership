.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

======================
Sale Create Membership
======================

* When a sales order is confirmed, if there are membership products on the order lines a membership contract is automatically created.
* A membership type can be defined for a membership product, which tells to whom the contract is created (company as well as person or just person).
* In the case of a company, a contract is created first for the company and then for the contact person. Only free products of the membership product will be imported into the contact person contract
* The contract and invoice are automatically linked when the invoice is created from the sales order.
* The membership price list is automatically added to the contract contact person.
* If contract template has been created then all its values are taken for the new contract .


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

.. image:: https://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: https://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
