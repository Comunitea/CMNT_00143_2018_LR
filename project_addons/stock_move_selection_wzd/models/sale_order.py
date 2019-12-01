# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
import odoo.addons.decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)

class ResCompany(models.Model):

    _inherit = 'res.company'

    @api.multi
    def cancel_orders(self):
        sales = self.env['sale.order'].search([('state', '=', 'sale')])
        _logger.info('\n-------------------\nVENTAS\n-------------------')
        for sale in sales:
            _logger.info('Procesando venta{}'.format(sale.name))
            try:
                sale.action_cancel()
            except:
                _logger.info('No se ha podido cancelar la venta {}'.format(sale.name))
        purchases = self.env['purchase.order'].search([('state', '!=', 'purchase')])
        _logger.info('\n-------------------\nCOMPRAS\n-------------------')
        for purchase in purchases:
            _logger.info('Procesando compra{}'.format(purchase.name))
            try:
                purchase.button_cancel()
            except:
                _logger.info('No se ha podido cancelar la compra {}'.format(purchase.name))

        pickings = self.env['stock.picking'].search([('state', 'not in', ('done', 'cancel'))])
        _logger.info('\n-------------------\nPICKS\n-------------------')
        for pick in pickings:
            _logger.info('Procesando pick {}'.format(pick.name))
            try:
                pick.action_cancel()
            except:
                _logger.info('No se ha podido cancelar el albaran {}'.format(pick.name))

        moves = self.env['stock.move'].search([('state', 'not in', ('done', 'cancel'))])
        _logger.info('\n-------------------\nMOVES\n-------------------')
        for move in moves:
            _logger.info('Procesando movimiento{}'.format(move.name))
            try:
                move.action_cancel_for_pda()
            except:
                _logger.info('No se ha podido cancelar el movimiento {}'.format(move.name))

        batchs = self.env['stock.batch.picking'].search([('state', '!=', 'done')])
        _logger.info('\n-------------------\nBATCHS\n-------------------')
        for batch in batchs:
            _logger.info('Procesando batc h{}'.format(batch.name))
            try:
                batch.unlink()
            except:
                _logger.info('No se ha podido eliminar el batch {}'.format(batch.name))

        batchs = self.env['stock.batch.delivery'].search([('state', '!=', 'done')])
        _logger.info('\n-------------------\nDELIVER\n-------------------')
        for batch in batchs:
            _logger.info('Procesando orden de carga{}'.format(batch.name))
            try:
                batch.unlink()
            except:
                _logger.info('No se ha podido eliminar el batch {}'.format(batch.name))

        return True

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_available_global = fields.Float(related='product_id.qty_available_global')

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def get_new_vals(self):
        return super().get_new_vals()

    @api.multi
    #@api.depends('order_line.move_ids.batch_picking_ids', 'order_line.move_ids.batch_delivery_ids')
    def get_batch_ids(self):

        for order in self:
            domain = order.get_moves_domain()
            move_ids = self.env['stock.move'].search(domain)
            order.batch_picking_ids = move_ids.mapped('batch_id')
            order.batch_delivery_ids = move_ids.mapped('batch_delivery_id')
            order.count_batch_picking_ids = len(order.batch_picking_ids)
            order.count_batch_delivery_ids = len(order.batch_delivery_ids)

    batch_picking_ids = fields.One2many('stock.batch.picking', compute=get_batch_ids)
    batch_delivery_ids = fields.One2many('stock.batch.delivery', compute=get_batch_ids)
    count_batch_picking_ids = fields.Integer(compute=get_batch_ids)
    count_batch_delivery_ids = fields.Integer(compute=get_batch_ids)

    @api.multi
    def action_view_batch_picking_ids(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_batch_picking.action_stock_batch_picking_tree').read()[0]
        action['domain'] = [('id', 'in', self.batch_picking_ids.ids)]
        return action

    @api.multi
    def action_view_batch_delivery_ids(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_move_selection_wzd.action_stock_batch_delivery_tree').read()[0]
        action['domain'] = [('id', 'in', self.batch_delivery_ids.ids)]
        return action

    @api.multi
    def action_view_move_lines(self):
        self.ensure_one()
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_action').read()[0]
        action['domain'] = self.get_moves_domain()
        action['context'] = {
            'group_code': 'picking',
            'search_default_by_type': True
            }


        return action

