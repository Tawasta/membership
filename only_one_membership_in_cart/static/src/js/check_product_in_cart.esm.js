/** @odoo-module **/

import {WebsiteSale} from "@website_sale/js/website_sale";

WebsiteSale.include({
    _onChangeCombination: function (ev, $parent) {
        console.log("on change in membership REACHED");

        const res = this._super.apply(this, arguments);

        const productId = $parent.find(".product_id").val();
        const route = `/check_product_in_cart`;

        this.rpc(route, {
            product_id: productId,
        }).then(function (response) {
            if (response.in_cart) {
                $parent.find("#add_to_cart").addClass("disabled");
                $parent.find(".o_we_buy_now").addClass("disabled");
            }

            return res;
        });
    },
});

export default WebsiteSale;
