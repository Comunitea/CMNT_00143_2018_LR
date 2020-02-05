# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

TYPES = [('order', 'Pedidos'), ('move', 'Movimientos'), ('picking', 'Albarán'), ('package', 'Paquetes'), ('partner', 'Clientes')]

class SBDFWMoveLine(models.TransientModel):
    _name = 'sbdfw.move.line'

    wzd_id = fields.Many2one('stock.batch.delivery.filter.wzd')
    type = fields.Selection(TYPES)
    name = fields.Char('Nombre')
    total = fields.Float('Importe')
    qty = fields.Float('Cantidad')

    partner_id = fields.Many2one('res.partner', 'Partner')
    package_id = fields.Many2one('stock.quant.package', 'Paquete')
    move_id = fields.Many2one('stock.move', 'Movimiento')
    picking_id = fields.Many2one('stock.picking', 'Albarán')
    sale_id = fields.Many2one(related='picking_id.sale_id', string='Venta')
    batch_picking_id = fields.Many2one('stock.batch.picking')

class StockBatchDeliveryFilterWzd(models.TransientModel):
    """Create a stock.batch.delivery from stock.moves or stock.quant.packages
    """
    _name = 'stock.batch.delivery.filter.wzd'
    _description = 'Asistente para orden de carga'

    delivery_id = fields.Many2one('stock.batch.delivery', string="Orden de carga", domain = [('state', '=', 'draft')])
    date = fields.Date(
        'Fecha', required=True, index=True, default=fields.Date.context_today,
        help='Date on which the batch picking is to be processed')
    picker_id = fields.Many2one('res.users', string='Usuario')
    type = fields.Selection(TYPES)

    shipping_type_ids = fields.Selection(SHIPPING_TYPE_SEL,
                                     default=DEFAULT_SHIPPING_TYPE,
                                     string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_ids = fields.Many2one('delivery.route.path', string="Route path")
    partner_ids = fields.Many2many('res.partner')


    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    driver_id = fields.Many2one('res.partner',
                                string='Conductor',
                                help='Conductor.',
                                domain="[('route_driver', '=', True)]")

    plate_id = fields.Many2one('delivery.plate', string='Matrícula', help='Matrícula.')
    move_ids = fields.Many2many('stock.move', string='Movimientos')
    picking_ids = fields.Many2many('stock.picking', string='Pedidos asociados', compute='get_child_vals')
    packages_ids = fields.Many2many('stock.quant.package', string='Paquetes', compute='get_child_vals')
    batch_ids = fields.Many2many('stock.')
    line_ids = fields.One2many('sbdfw.move.line', 'wzd_id')
    warning = fields.Char ('Warning')


    def refresh(self):
        move_line_ids = self.env['stock.move.line'].search(self.get_domain())
        if self.type=='move':
            move_ids = move_line_ids.mapped('move_id')
            self.line_ids.unlink()
            for move in move_ids:
                picking_id = move.picking_id
                val = {'move_id': move.id,
                       'type': self.type,
                       'name': move.product_id.display_name,
                       'product_id': move.product_id.id,
                       'partner_id': move.partner_id.id,
                       'picking_id': picking_id.id,
                       'batch_picking_id': picking_id.batch_picking_id and picking_id.batch_picking_id.id,
                       'package_id': move.move_line_ids.mapped('result_package_id'),
                       'shipping_type': move.shipping_type,
                       'delivery_route_path_id': move.delivery_route_path_id.id,
                       }
                self.write({'line_ids': [(0, 0, val)]})
        elif self.type == 'order':
            picking_ids = move_line_ids.mapped('move_id').mapped('picking_id')
            self.line_ids.unlink()
            for pick in picking_ids:

                val = {'picking_id': pick.id,
                       'type': self.type,
                       'name': pick.sale_id.name,
                       #'product_id': move.product_id.id,
                       'partner_id': pick.partner_id.id,
                       'total': pick.sale_id.total_amount,
                       'batch_picking_id': pick.batch_picking_id and pick.batch_picking_id.id,
                       #'package_id': move.move_line_ids.mapped('result_package_id'),
                       'shipping_type': pick.shipping_type,
                       'delivery_route_path_id': pick.delivery_route_path_id.id,
                       }
                self.write({'line_ids': [(0, 0, val)]})
        elif self.type == 'package':
            package_ids = move_line_ids.mapped('result_package_id')

            self.line_ids.unlink()
            for pack in package_ids:
                val = {'package_id': pack.id,
                       'type': self.type,
                       'name': pack.name,
                       # 'product_id': move.product_id.id,
                       'partner_id': pack.partner_id.id,

                       #'batch_picking_id': pack.picking_id.batch_picking_id and pick.batch_picking_id.id,
                       # 'package_id': move.move_line_ids.mapped('result_package_id'),
                       'shipping_type': pack.shipping_type,
                       'delivery_route_path_id': pack.delivery_route_path_id.id,
                       }
                self.write({'line_ids': [(0, 0, val)]})



    def get_domain(self):

        if self.with_package == '0':
            domain = [('result_package_id', '=', False)]
        elif self.with_package == '1':
            domain = [('result_package_id', '!=', False)]
        else:
            domain = []

        if self.shipping_type_ids:
            shipping_type_ids = self.shipping_type_ids.mapped('code')
            domain += [('move_id.shipping_type', 'in', shipping_type_ids)]
        if self.delivery_route_path_ids:
            route_path_ids = self.delivery_route_path_ids.ids
            domain += [('move_id.delivery_route_path_id', 'in', route_path_ids)]
        if self.partner_ids:
            partner_ids = self.partner_ids.ids
            domain += [('move_id.partner_id', 'in', partner_ids)]


