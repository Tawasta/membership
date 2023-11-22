odoo.define("website_sale_family_membership.CustomWebsiteSale", function (require) {
    "use strict";

    var publicWidget = require("web.public.widget");
    var WebsiteSale = publicWidget.registry.WebsiteSale;
    var ajax = require("web.ajax");
    const wUtils = require("website.utils");

    WebsiteSale.include({
        _submitForm: function () {
            var self = this;
            var _super = this._super.bind(this);
            var selectedOption = $(".form-control.js_variant_change.always").find(
                ":selected"
            );
            var selectedAttributeValue = selectedOption.val();
            var dataValueName = selectedOption.data("value_name");

            // Tehdään tarkistus onko kyseisellä atribuutilla family membership sääntö
            this.checkIfFamilyRule(selectedAttributeValue, function (isFamily) {
                if (isFamily) {
                    ajax.jsonRpc("/get_updated_modal_content", "call", {
                        counterValue: parseInt(dataValueName),
                    }).then(function (modalContent) {
                        $("#familyMemberModal .modal-body").html(modalContent);
                        var $modal = $("#familyMemberModal");
                        $modal.modal("show");

                        // Käsitellään modalin tallennus ja datan keräys
                        var $save_button = $("#saveFamilyMemberButton");
                        $save_button.off("click").on("click", function () {
                            var formData = {};
                            $("#familyMemberModal .modal-body .form-group").each(
                                function () {
                                    var input = $(this).find("input");
                                    var inputName = input.attr("name");
                                    var inputValue = input.val();

                                    // Erotetaan indeksi ja kentän tyyppi (esim. '0-firstname')
                                    var matches = inputName.match(/(\d+)-(\w+)/);
                                    if (matches) {
                                        var index = matches[1];
                                        var field = matches[2];

                                        // Luo uusi objekti jokaiselle perheenjäsenelle
                                        formData[index] = formData[index] || {};
                                        formData[index][field] = inputValue;
                                    }
                                }
                            );

                            const params = self._prepareParams();
                            // Serialisoi familyMembers-objekti JSON-muotoon
                            params.familyMembers = JSON.stringify(formData);
                            // Lähetä päivitetyt tiedot palvelimelle
                            return wUtils.sendRequest("/shop/cart/update", params);
                        });
                    });
                } else {
                    _super.apply(this, arguments);
                }
            });
        },

        checkIfFamilyRule: function (selectedAttributeValue, callback) {
            ajax.jsonRpc("/check_attribute", "call", {
                selectedAttributeValue: selectedAttributeValue,
            }).then(function (response) {
                callback(response.is_family);
            });
        },

        _prepareParams: function () {
            const params = this.rootProduct;
            params.add_qty = params.quantity;
            params.product_custom_attribute_values = JSON.stringify(
                params.product_custom_attribute_values
            );
            params.no_variant_attribute_values = JSON.stringify(
                params.no_variant_attribute_values
            );

            if (this.isBuyNow) {
                params.express = true;
            }

            return params;
        },
    });
});
