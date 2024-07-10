/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";

publicWidget.registry.only_one_membership_in_cart = publicWidget.Widget.extend({
    selector: "#product_details",

    events: {
        "change input.product_id": "_checkProductAndBlockIfNeeded",
    },

    init: function () {
        this.rpc = this.bindService("rpc");
        this._checkProductAndBlockIfNeeded();
    },

    _checkProductAndBlockIfNeeded: async function () {
        var $button = $("#add_to_cart");
        if ($button.length) {
            // Haetaan productId .product_id kentästä
            const productId = $("#product_details .js_main_product .product_id").val();

            var isInCart = this._checkIfProductInCart(productId);

            const inCartResult = await Promise.resolve(isInCart);
            const inCart = inCartResult.in_cart;

            if (inCart) {
                $("#add_to_cart").addClass("disabled");
                $(".o_we_buy_now").addClass("disabled");
            }
        }
    },

    _checkIfProductInCart: function (productId) {
        var result = this.rpc("/check_product_in_cart", {
            product_id: productId,
        });
        return result;
    },
});
