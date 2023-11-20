odoo.define('only_one_membership_in_cart.product_cart_check', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var checkProductAvailability = require('product_cant_order.product').checkProductAvailability;

    $(document).ready(function () {
        var $button = $('#add_to_cart');
        checkProductAndBlockIfNeeded($button);

        $('.variant_attribute select').on('change', function () {
            // Asetetaan pieni viive varmistaaksemme, että arvo on ehtinyt vaihtua
            setTimeout(function() {
                checkProductAndBlockIfNeeded($button);
            }, 160);
        });


        function checkProductAndBlockIfNeeded($button) {
            if ($button.length) {
                var productId = $button.closest('.oe_website_sale').find('.product_id').val();

                // Ensin suoritetaan peritty checkProductAvailability-funktio
                checkProductAvailability(productId, function (availabilityResult) {
                    // Sitten tämän moduulin toiminnallisuus
                    checkIfProductInCart(productId, function (isInCart) {
                        if (isInCart) {
                            $("#add_to_cart").addClass("blocked");
                            $("#buy_now").addClass("blocked");
                        } else {
                            $("#add_to_cart").removeClass("blocked");
                            $("#buy_now").removeClass("blocked");
                        }
                    });
                });
            }
        }

        function checkIfProductInCart(productId, callback) {
            ajax.jsonRpc('/check_product_in_cart', 'call', {'product_id': productId})
                .then(function (response) {
                    callback(response.in_cart);
                });
        }
    });
});


