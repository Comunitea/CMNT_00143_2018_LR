/* odoo.define('website_sale.shop_event_manager', function (require) {
    "use strict";
    
    var Class = require('web.Class');
    var rpc = require('web.rpc');

var shopEventManager = Class.extend({

    start: function () {
        return this._super.apply(this, arguments);
    },

    _render_barcode: function(event) {
        event.preventDefault();
        console.log(event);
        var self = this;
        var id = $(event.target).closest('tr').attr('id');
        rpc.query({
                model: 'product.template',
                method: 'search_read',
                domain: [['id', '=', id]],
                fields: [
                    "barcode",
                    "display_name",
                ],
            })
            .then(function (data) {
                console.log(data);
                this._render_modal(data[0], 'barcode');
            });
    },

    _render_image: function(event) {
        event.preventDefault();
        var self = this;
        var id = $(event.target).closest('tr').attr('id');
        rpc.query({
                model: 'product.template',
                method: 'search_read',
                domain: [['id', '=', id]],
                fields: [
                    "id",
                    "image",
                    "display_name",
                ],
            })
            .then(function (data) {
                console.log(data);
                this._render_modal(data[0], 'image');
            });
    },

    _render_modal: function (data, type) {
        var modal_content = '';

        if (type == 'barcode') {

            if (data[0]['barcode'].length == 13){
                modal_content = '<img src="/report/barcode/?type=EAN13&value='+data[0]['barcode']+'&width=600&height=150" style="width:100%;height:20%;" />';
            } else if (data['barcode'] == 8) {
                modal_content = '<img src="/report/barcode/?type=EAN8&value='+data[0]['barcode']+'&width=600&height=150" style="width:100%;height:20%;" />';
            } else {
                modal_content = '<img src="/report/barcode/?type=Code128&value='+data[0]['barcode']+'&width=600&height=150" style="width:100%;height:20%;" />';
            }

        } else if (type == 'image') {

            modal_content = '<img src="/website/image/product.template/'+data[0]['id']+'/image" alt="'+data[0]['display_name']+'"></img>';

        }

        var html =  '<div class="modal fade" id="modalWindow" tabindex="-1" role="dialog" aria-labelledby="modalLabel" aria-hidden="true">';
        html += '<div class="modal-dialog" role="document">';
        html += '<div class="modal-content">';
        html += '<div class="modal-header">';
        html += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
        html += '<span aria-hidden="true">&times;</span>';
        html += '</button>';
        html += '<h4 class="modal-title" id="modalLabel">'+data[0]['display_name']+'</h4>'
        html += '</div>';
        html += '<div class="modal-body text-center">';
        html += modal_content;
        html += '<div class="modal-footer">';
        html += '<button class="btn btn-secondary" data-dismiss="modal">';
        html += 'Close';
        html += '</button>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        html += '</div>';
        $("#rpc_modal").html(html);
        $("#modalWindow").modal();
    },


});

return shopEventManager;

}); */

odoo.define('theme_rias.website_sale', function(require) {

    var rpc = require('web.rpc');
    require('web.dom_ready');
    require('website_sale.website_sale');
    var ajax = require('web.ajax');
    var core = require('web.core');
    require("website.content.zoomodoo");
    var _t = core._t;



    $(".oe_website_sale").on('click', 'a.barcode-call', function (event) {
        event.preventDefault();
        var product_id = $(event.target).closest('tr').attr('product-id');
        var variant_id = $(event.target).closest('tr').attr('variant-id');
        var model = 'product.template';

        if (variant_id == true) {
            model = 'product.product';
            product_id = variant_id;
        }

        rpc.query({
            model: model,
            method: 'search_read',
            domain: [['id', '=', product_id]],
            fields: [
                "barcode",
                "display_name",
            ]})
            .then(function(data){
                if (data[0]['barcode'].length == 13){
                    modal_content = '<img src="/report/barcode/?type=EAN13&value='+data[0]['barcode']+'&width=600&height=150" style="width:100%;height:20%;" />';
                } else if (data['barcode'] == 8) {
                    modal_content = '<img src="/report/barcode/?type=EAN8&value='+data[0]['barcode']+'&width=600&height=150" style="width:100%;height:20%;" />';
                } else {
                    modal_content = '<img src="/report/barcode/?type=Code128&value='+data[0]['barcode']+'&width=600&height=150" style="width:100%;height:20%;" />';
                }

                var html =  '<div class="modal fade" id="modalWindow" tabindex="-1" role="dialog" aria-labelledby="modalLabel" aria-hidden="true">';
                html += '<div class="modal-dialog" role="document">';
                html += '<div class="modal-content">';
                html += '<div class="modal-header">';
                html += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
                html += '<span aria-hidden="true">&times;</span>';
                html += '</button>';
                html += '<h4 class="modal-title" id="modalLabel">'+data[0]['display_name']+'</h4>'
                html += '</div>';
                html += '<div class="modal-body text-center">';
                html += modal_content;
                html += '<div class="modal-footer">';
                html += '<button class="btn btn-secondary" data-dismiss="modal">';
                html += 'Close';
                html += '</button>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
                $("#rpc_modal").html(html);
                $("#modalWindow").modal();
            });
    });

    $(".oe_website_sale").on('click', 'a.image-call', function (event) {
        event.preventDefault();
        var product_id = $(event.target).closest('tr').attr('product-id');
        var variant_id = $(event.target).closest('tr').attr('variant-id');

        var model = 'product.template';

        if (variant_id == true) {
            model = 'product.product';
            product_id = variant_id;
        }

        rpc.query({
            model: model,
            method: 'search_read',
            domain: [['id', '=', product_id]],
            fields: [
                "id",
                "image",
                "display_name",
            ]})
            .then(function(data){
                modal_content = '<img src="/website/image/product.template/'+data[0]['id']+'/image" alt="'+data[0]['display_name']+'"></img>';

                var html =  '<div class="modal fade" id="modalWindow" tabindex="-1" role="dialog" aria-labelledby="modalLabel" aria-hidden="true">';
                html += '<div class="modal-dialog" role="document">';
                html += '<div class="modal-content">';
                html += '<div class="modal-header">';
                html += '<button type="button" class="close" data-dismiss="modal" aria-label="Close">';
                html += '<span aria-hidden="true">&times;</span>';
                html += '</button>';
                html += '<h4 class="modal-title" id="modalLabel">'+data[0]['display_name']+'</h4>'
                html += '</div>';
                html += '<div class="modal-body text-center">';
                html += modal_content;
                html += '<div class="modal-footer">';
                html += '<button class="btn btn-secondary" data-dismiss="modal">';
                html += 'Close';
                html += '</button>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
                html += '</div>';
                $("#rpc_modal").html(html);
                $("#modalWindow").modal();
            });
    });   

});



odoo.define('website_sale.website_sale', function (require) {
    "use strict";

    require('web.dom_ready');
    var ajax = require('web.ajax');
    var core = require('web.core');
    require("website.content.zoomodoo");
    var _t = core._t;

    var clickwatch = (function(){
        var timer = 0;
        return function(callback, ms){
          clearTimeout(timer);
          timer = setTimeout(callback, ms);
        };
    })();

    $('.oe_website_sale').off("change", "input.js_quantity[data-product-id]").on("change", "input.js_quantity[data-product-id]", function () {
        var $input = $(this);
        if ($input.data('update_change') || $('body').hasClass('editor_enable')) {
            return;
        }
        var value = parseInt($input.val() || 0, 10);
        if (isNaN(value)) {
            value = 1;
        }
        var $dom = $(this).closest('tr');
        //var default_price = parseFloat($dom.find('.text-danger > span.oe_currency_value').text());
        var $dom_optional = $dom.nextUntil(':not(.optional_product.info)');
        var line_id = parseInt($input.data('line-id'),10);
        var product_ids = [parseInt($input.data('product-id'),10)];
        clickwatch(function(){
            $dom_optional.each(function(){
                $(this).find('.js_quantity').text(value);
                product_ids.push($(this).find('span[data-product-id]').data('product-id'));
            });
            $input.data('update_change', true);

            ajax.jsonRpc("/shop/cart/update_json", 'call', {
                'line_id': line_id,
                'product_id': parseInt($input.data('product-id'), 10),
                'set_qty': value
            }).then(function (data) {
                $input.data('update_change', false);
                var check_value = parseInt($input.val() || 0, 10);
                if (isNaN(check_value)) {
                    check_value = 1;
                }
                if (value !== check_value) {
                    $input.trigger('change');
                    return;
                }
                var $q = $(".my_cart_quantity");
                if (data.cart_quantity) {
                    $q.parents('li:first').removeClass("hidden");
                }
                else {
                    $q.parents('li:first').addClass("hidden");
                    $('a[href*="/shop/checkout"]').addClass("hidden");
                }

                $q.html(data.cart_quantity).hide().fadeIn(600);
                $input.val(data.quantity);
                $('.js_quantity[data-line-id='+line_id+']').val(data.quantity).html(data.quantity);

                $(".js_cart_lines").first().before(data['website_sale.cart_lines']).end().remove();

                if (data.warning) {
                    var cart_alert = $('.oe_cart').parent().find('#data_warning');
                    if (cart_alert.length === 0) {
                        $('.oe_cart').prepend('<div class="alert alert-danger alert-dismissable" role="alert" id="data_warning">'+
                                '<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning + '</div>');
                    }
                    else {
                        cart_alert.html('<button type="button" class="close" data-dismiss="alert" aria-hidden="true">&times;</button> ' + data.warning);
                    }
                    $input.val(data.quantity);
                }
          });
        }, 500);

        if (value > 0) {
            $dom.find('.js_delete_product').removeClass('hidden');
        } else {
            $dom.find('.js_delete_product').addClass('hidden');
        }
    });

    $(".oe_website_sale").on('click', '.js_delete_product', function(e) {
        e.preventDefault();
        $(this).closest('tr').find('.js_quantity').val(0).trigger('change');
    });

    // hack to add and remove from cart with json
    $('.oe_website_sale').off('click', 'a.js_add_cart_json').on('click', 'a.js_add_cart_json', function (ev) {
        if ($('body').hasClass('editor_enable')) {
            return;
        }
        ev.preventDefault();
        var $link = $(ev.currentTarget);
        var $input = $link.parent().find("input");
        var product_id = +$input.closest('*:has(input[name="product_id"])').find('input[name="product_id"]').val();
        var min = parseFloat($input.data("min") || 0);
        var max = parseFloat($input.data("max") || Infinity);
        var quantity = ($link.has(".fa-minus").length ? -1 : 1) + parseFloat($input.val() || 0, 10);
        var new_qty = quantity > min ? (quantity < max ? quantity : max) : min;
        // if they are more of one input for this product (eg: option modal)
        $('input[name="'+$input.attr("name")+'"]').add($input).filter(function () {
            var $prod = $(this).closest('*:has(input[name="product_id"])');
            return !$prod.length || +$prod.find('input[name="product_id"]').val() === product_id;
        }).val(new_qty).change();
        return false;
    });


    // Checking if the product is allowed in the cart

    $(document).ready(function() {

        /* if ($('#wrapwrap').hasClass('shoppage')) {
            $(".oe_website_sale").on('click', 'a.campaign-call', function (event) {
                event.preventDefault();
                var campaign_id = parseInt($(event.target).parent().attr('data-campaign-id'));
                console.log($(event.target).parent().attr('data-campaign-id'));
                console.log($(event.target).closest('a').attr('data-campaign-id'));
                console.log($(event.target).attr('data-campaign-id'));
                console.log(campaign_id);
                var variant_id = parseInt($(event.target).closest('tr').attr('variant-id'));

                if (variant_id == true) {
                    product_id = variant_id;
                }
                var $input = $(event.target).closest('tr').find("input");
                ajax.jsonRpc("/shop/cart/add_to_campaign_json", 'call', {
                    'campaign_id': campaign_id,
                    'product_id': parseInt($input.data('product-id'), 10),
                    'set_qty': 1
                }).then(function (data) {
                    console.log(data);
                });
            });
        } */

        if ($('#wrapwrap').hasClass('productpage')) {
            var is_allowed = $('#allowed_purchase').text();
            if (is_allowed == 'denied') {
                $('#add_to_cart').remove();
                $('.css_quantity').remove();
                $('#purchase_msg').html('<div class="alert alert-danger" role="alert">'+
                'Este producto no pertenece a la campaña del pedido actual.</div>');
            } else if (is_allowed == 'warning') {
                $('#purchase_msg').html('<div class="alert alert-warning" role="alert">'+
                'Este producto pertenece a una campaña activa, te recomendamos añadirlo a un pedido de campaña.'+
                '</div>');
            }

            function calculate_if_allowed() {
                var prod_id = parseInt($('input[name="product_id"]').attr('value'));
                ajax.jsonRpc("/shop/cart/is_allowed_purchase_json", 'call', {
                    'product_id': prod_id,
                }).then(function (data) {
                    if (data['status'] == 'denied') {
                        $('#add_to_cart').addClass('hidden');
                        $('.css_quantity').addClass('hidden');
                        $('#purchase_msg').html('<div class="alert alert-danger" role="alert">'+
                        'Este producto no pertenece a la campaña del pedido actual.</div>');
                    } else if (data['status'] == 'warning') {
                        $('#add_to_cart').removeClass('hidden');
                        $('.css_quantity').removeClass('hidden');
                        $('#purchase_msg').html('<div class="alert alert-warning" role="alert">'+
                        'Este producto pertenece a una campaña activa, te recomendamos añadirlo a un pedido de campaña.</div>');
                    } else if (data['status'] == 'allowed') {
                        $('#add_to_cart').removeClass('hidden');
                        $('.css_quantity').removeClass('hidden');
                        $('#purchase_msg').html('');
                    }
                });
            }

            $(".oe_website_sale").on('change', 'input[name="product_id"]', function() {
                calculate_if_allowed();
            });

            $(".oe_website_sale").on('change', '.js_variant_change', function(e) {
                $('input[name="product_id"]').trigger('change');
            });
            
        }

        if ($('#wrapwrap').hasClass('wishlistpage')) {
            
            $('tr').each(function() {
                var is_allowed = $(this).find('td:nth-child(2)').find('.allowed_purchase').text();
                if (is_allowed == 'denied') {
                    $(this).find('td:last()').find('input').remove();
                    $(this).find('td:last()').find('a').remove();
                    $(this).find('td:nth-child(2)').find('.purchase_msg').html('<div class="alert alert-danger" role="alert">Este producto no pertenece a la campaña del pedido actual.</div>');
                } else if (is_allowed == 'warning') {
                    $(this).find('td:nth-child(2)').find('.purchase_msg').html('<div class="alert alert-warning" role="alert">Este producto pertenece a una campaña activa, te recomendamos añadirlo a un pedido de campaña.</div>');
                }
            });

        }

    });
});