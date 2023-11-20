odoo.define('only_one_membership_in_cart.product_cart_check', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var checkProductAvailability = require('product_cant_order.product').checkProductAvailability;

    function checkProductAndBlockIfNeeded($button) {
        if ($button.length) {
            var productId = $('.product_id').val(); // Haetaan productId .product_id kentästä

            checkProductAvailability(productId, function (availabilityResult) {
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

    $(document).ready(function () {
        var $button = $('#add_to_cart');
        checkProductAndBlockIfNeeded($button);

        // Tapahtumankäsittelijä .product_id kentälle
        $('.product_id').on('change', function() {
            checkProductAndBlockIfNeeded($button);
        });
    });

    // Oletettu funktio, joka päivittää .product_id:n arvon
    function updateProductId(newProductId) {
        $('.product_id').val(newProductId).trigger('change');
    }

    return {
        checkProductAvailability: checkProductAvailability,
        updateProductId: updateProductId
    };
});
