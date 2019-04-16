# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import UserError

from pprint import pprint

class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    @api.multi
    def get_result_package_ids(self):
        self.ensure_one()
        packages = self.move_line_ids.mapped('result_package_id')
        self.current_package_list = [(6,0,packages.ids)]

    carrier_id = fields.Many2one(
        'delivery.carrier', string='Delivery carrier', track_visibility='onchange',
        help='Delivery carrier for this batch picking.')
    carrier_partner_id = fields.Many2one(
        'res.partner', string='Carrier driver', track_visibility='onchange',
        help='Carrier driver for this batch picking.', domain="[('delivery_id', '=', carrier_id)]")
    delivery_route_id = fields.Many2one(
        'delivery.route.path', string='Delivery route', track_visibility='onchange',
        help='Delivery route for this batch picking.')
    shipping_type = fields.Selection(
        [('pasaran', 'Pasarán'),
         ('agency', 'Agencia'),
         ('route', 'Ruta')],
        string='Tipo de envío',
        help="Tipo de envío seleccionado."
    )
    has_packages = fields.Boolean(
        'Has Packages', compute='_compute_has_packages',
        help='Check the existence of destination packages on move lines')
    #packages_added_manually = fields.One2many('stock.quant.package', 'stock_batch_id', 'Quants')
    current_package_list = fields.One2many('stock.quant.package', compute="get_result_package_ids", string="Packages")
    current_location_id = fields.Many2one(
        string='Location',
        comodel_name='stock.location',
        compute="check_batch_location_ids"
    )
    current_location_dest_id = fields.Many2one(
        string='Location Dest',
        comodel_name='stock.location',
        compute="check_batch_location_ids"
    )

    @api.model
    def check_batch_location_ids(self):
        for batch in self:
            batch.current_location_id = batch.mapped('move_line_ids').mapped('location_id').id
            batch.current_location_dest_id = batch.mapped('move_line_ids').mapped('location_dest_id').id

    @api.onchange('shipping_type')
    def onchange_shipping_type(self):
        if self.shipping_type == 'pasaran' or self.shipping_type == 'route':
            self.carrier_id = False

    @api.multi
    def action_see_packages(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update(stock_batch_id= self.id)
        ctx.update(shipping_type= self.shipping_type)
        ctx.update(current_location_id= self.current_location_id.id)
        ctx.update(current_location_dest_id= self.current_location_dest_id.id)
        action = self.env.ref('stock_batch_picking_lr.action_package_delivery_batch_view').read()[0]
        move_lines_ids = self.picking_ids.mapped('move_line_ids').search([('location_dest_id', '=', self.current_location_dest_id.id),('location_id', '=', self.current_location_id.id)])
        packages = move_lines_ids.mapped('result_package_id').search([('shipping_type', '=', self.shipping_type),'|',('stock_batch_id', '=', self.id),('stock_batch_id', '=', False)])
        action['domain'] = [('id', 'in', packages.ids)]
        action['context'] = ctx
        return action

    @api.multi
    def _compute_has_packages(self):
        count = 0
        for picking in self:
            if picking.move_line_ids.mapped('result_package_id'):
                count = count +1
        if count is not 0:
            self.has_packages = True
        else:
            self.has_packages = False
    
    @api.multi
    def batch_printing(self):

        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)

            return self.env.ref('stock_batch_picking_lr.delivery_batch_report').with_context(active_ids=active_ids, active_model='stock.batch.picking', pickings=pickings).report_action([])