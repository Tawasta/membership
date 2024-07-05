/** @odoo-module **/

import publicWidget from "@web/legacy/js/public/public_widget";
//import.product_cant_order from "@product_cant_order/static/js/product_cart.esm";

publicWidget.registry.only_one_membership_in_cart = publicWidget.Widget.extend({
    selector: "#product_details",

    events: {
        "change input.product_id": "_checkProductAndBlockIfNeeded",
    },

    init: function () {
        //var $button = $("#add_to_cart");
        this.rpc = this.bindService("rpc");
        this._checkProductAndBlockIfNeeded();
    },

//    var checkProductAvailability =
//        require("product_cant_order.product").checkProductAvailability;
//
    _checkProductAndBlockIfNeeded: async function () {
        var $button = $("#add_to_cart");
        if ($button.length) {
            // Haetaan productId .product_id kentästä
            const productId = $("#product_details .js_main_product .product_id").val();

            //checkProductAvailability(productId, function (availabilityResult) {
            const isInCart = this._checkIfProductInCart(productId);

            //_checkIfProductInCart(productId, function (isInCart) {
            if (isInCart) {
                $("#add_to_cart").addClass("blocked");
                $(".o_we_buy_now").addClass("blocked");
            } else {
                $("#add_to_cart").removeClass("blocked");
                $(".o_we_buy_now").removeClass("blocked");
            }
            //});
            //});
        }
    },

    _checkIfProductInCart: async function (productId) {
        var result = this.rpc("/check_product_in_cart", {
            product_id: productId
        });
        result.then((res) => {
            return res.in_cart
        });
    },

    // Oletettu funktio, joka päivittää .product_id:n arvon
    //function updateProductId(newProductId) {
    //    $(".product_id").val(newProductId).trigger("change");
    //}

    //return {
    //    checkProductAvailability: checkProductAvailability,
    //    updateProductId: updateProductId,
    //};
});
