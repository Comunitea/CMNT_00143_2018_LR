# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _

class StockPackOperationSGA(models.Model):

    _inherit = "stock.move.line"
    _order = "result_package_id desc, line_number asc, id"

    product_code = fields.Char(related="product_id.default_code")
    line_number = fields.Integer("Number de linea")
    sga_catch_weight = fields.Selection([('1', 'True'), ('0', 'False')], 'Catch weight',
                                        help="1 Indica si se captura el peso del producto\n"
                                             "0 (por defecto) se coge el peso de la ficha de producto", default='0')
    sga_sustitute_qty = fields.Float("Sustitute qty", help="Si se informa sustitute_prod_code, es la cantidad\n"
                                                           "de producto a sustituir", default=0)
    sga_disable_alt_product = fields.Selection([('1', 'True'), ('0', 'False')], 'Disable alt product',
                                        help="1 Se deshabilita el producto alternativo\n"
                                             "0 (por defecto) No se deshabilita", default='1')
    sga_changed = fields.Boolean ('SGA modified/created', default=False)
    product_tmpl_id = fields.Many2one(related="product_id.product_tmpl_id")
    picking_id = fields.Many2one(related="move_id.picking_id")

    adaia_container = fields.Char()