odoo.define(
    "website_sale_membership_firstname2.show_firstname2_conditionally",
    function (require) {
        "use strict";

        var publicWidget = require("web.public.widget");
        var ajax = require("web.ajax");

        publicWidget.registry.FirstName2VisibilityHandler = publicWidget.Widget.extend({
            selector: ".oe_website_sale",

            start: function () {
                this._super.apply(this, arguments);
                this.checkFirstName2Visibility();
            },

            checkFirstName2Visibility: function () {
                var self = this;
                ajax.jsonRpc("/show_firstname2", "call", {}).then(function (result) {
                    self.toggleFirstName2Visibility(result.show);
                });
            },

            toggleFirstName2Visibility: function (show) {
                var $firstname2 = $(".div_firstname2");
                if (show) {
                    $firstname2.removeClass("d-none");
                } else {
                    $firstname2.addClass("d-none");
                }
            },
        });
    }
);
