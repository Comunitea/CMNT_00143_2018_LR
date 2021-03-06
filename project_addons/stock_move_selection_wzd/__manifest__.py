# -*- coding: utf-8 -*-
# © 2018 Comunitea - Kiko Sánchez <kiko@comunitea.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

{
    'name': 'Stock Move Selection Wzd',
    'version': '11.0.0.0.0',
    'category': 'Custom',
    'license': 'AGPL-3',
    'author': "Comunitea, ",
    'depends': [
        'sale_stock',
        'stock_picking_imp',
        'stock_picking_group',
        'stock_picking_type_group',
        'shipping_type',
        'stock_available_global',
        'purchase_sale_inter_company_custom',
        'stock_custom',
        'stock_picking_type_bookmark'
        #'portal'
    ],
    'data': [
        'data/stock_batch_picking_sequence.xml',
        'data/stock_batch_delivery.xml',
        'security/ir.model.access.csv',
        'report/report_delivery_batch_views.xml',
        'report/report_batch_picking.xml',
        'views/stock_batch_delivery.xml',
        #'views/delivery_route_path.xml',
        'views/picking_type.xml',
        'views/product.xml',
        'views/res_partner_views.xml',
        'views/stock_batch_picking_views.xml',
        'views/stock_move.xml',
        'views/sale_order.xml',
        'views/stock_picking.xml',
        'views/stock_quant_package.xml',
        'wizard/action_pack_move_wzd.xml',
        'wizard/batch_picking_wzd_view.xml',
        'wizard/batch_delivery_wzd_view.xml',
        'wizard/move_change_quant_wzd.xml',
        #'wizard/config_stock_delivery.xml',
        'wizard/batch_picking_excess.xml',
        'wizard/move_complete_package.xml',
        #'wizard/create_package_picking_from_package.xml',
        'views/menu_views.xml',
        'views/menu_views_stock_picking.xml',
    ],
    'installable': True,
}


