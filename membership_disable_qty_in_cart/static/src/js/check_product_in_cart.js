odoo.define('membership_disable_qty_in_cart.product_cart_check', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        var $button = $('#add_to_cart');
        if ($button.length) {
            var productId = $button.closest('.oe_website_sale').find('.product_id').val();
            checkIfProductInCart(productId, function (isInCart) {
                if (isInCart) {
                    $("#add_to_cart").addClass("blocked");
                    $("#buy_now").addClass("blocked");
                }
            });
        }

        function checkIfProductInCart(productId, callback) {
            // AJAX-kutsu Odoo-palvelimelle
            ajax.jsonRpc('/check_product_in_cart', 'call', {'product_id': productId})
                .then(function (response) {
                    callback(response.in_cart);
                })
        }
    });
});

