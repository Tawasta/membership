odoo.define('website_slides_cart.course_card', function (require) {
    "use strict";

    $(function () {

        $('.add_to_cart').on('click', function() {
            var $ele = $(this);
            $ele.closest('form').submit();
        });
    });
});
