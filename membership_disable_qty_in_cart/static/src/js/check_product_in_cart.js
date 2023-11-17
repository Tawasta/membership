odoo.define('membership_disable_qty_in_cart.product_cart_check', function (require) {
    'use strict';

    var ajax = require('web.ajax');

    $(document).ready(function () {
        var $button = $('#add_to_cart');
        checkProductAndBlockIfNeeded($button);

        $('.variant_attribute select').on('change', function () {
            checkProductAndBlockIfNeeded($button);
        });

        function checkProductAndBlockIfNeeded($button) {
            if ($button.length) {
                var productId = $button.closest('.oe_website_sale').find('.product_id').val();
                checkIfProductInCart(productId, function (isInCart) {
                    console.log(isInCart);
                    if (isInCart) {
                        $("#add_to_cart").addClass("blocked");
                        $("#buy_now").addClass("blocked");
                    } else {
                        $("#add_to_cart").removeClass("blocked");
                        $("#buy_now").removeClass("blocked");
                    }
                });
            }
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

