# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import UserError

class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    # @api.multi
    # def get_result_package_ids(self):
    #     self.ensure_one()
    #     packages = self.move_line_ids.mapped('result_package_id')
    #     self.current_package_list = [(6,0,packages.ids)]

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

    current_package_list = fields.One2many('stock.quant.package', "batch_picking_id", string="Packages")
    # current_location_id = fields.Many2one(
    #     string='Location',
    #     comodel_name='stock.location',
    #     compute="check_batch_location_ids"
    # )
    # current_location_dest_id = fields.Many2one(
    #     string='Location Dest',
    #     comodel_name='stock.location',
    #     compute="check_batch_location_ids"
    # )
    picking_type_id = fields.Many2one(
        string='Picking type',
        comodel_name='stock.picking.type',
    )

    #@api.model
    #def check_batch_location_ids(self):
    #    for batch in self:
    #        batch.current_location_id = batch.picking_type_id.default_location_src_id ## batch.picking_ids and batch.picking_ids[0].location_id or False
    #        batch.current_location_dest_id = batch.picking_type_id.default_location_src_id ## batch.picking_ids and batch.picking_ids[0].location_dest_id or False


    @api.onchange('shipping_type')
    def onchange_shipping_type(self):
        for package in self.current_package_list:
            if package.shipping_type != self.shipping_type:
                raise UserError(_('The selected shipping type is different from the shipping type of the packages. If you wish to change this batch shipping type you must remove the packages first.'))
        if self.shipping_type == 'pasaran' or self.shipping_type == 'route':
            self.carrier_id = False
            self.carrier_partner_id = False

    def get_domain_move(self):
        return [('state', 'not in', ['cancel', 'draft', 'done']),
                ('location_dest_id', 'child_of', self.picking_type_id.default_location_dest_id.id),
                ('location_id', 'child_of', self.picking_type_id.default_location_src_id.id)]

    def get_domain_package(self, move_line_ids):
        return [ '|',('batch_picking_id', '=', self.id),
                 ('id', 'in', move_line_ids),
                 ('shipping_type', '=', self.shipping_type),
                 ('batch_picking_id', '=', False)]
    @api.multi
    def action_see_packages(self):
        self.ensure_one()
        ctx = self._context.copy()
        ctx.update(batch_picking_id= self.id)
        ctx.update(shipping_type= self.shipping_type)
        #ctx.update(current_location_id=  self.picking_type_id.default_location_src_id.id)
        #ctx.update(current_location_dest_id= self.picking_type_id.default_location_dest_id.id)
        action = self.env.ref('stock_batch_picking_lr.action_package_delivery_batch_view').read()[0]
        domain_move = self.get_domain_move()
        move_lines_ids = self.env['stock.move.line'].search(domain_move)
        package_domain = self.get_domain_package(move_lines_ids.mapped('result_package_id').ids)
        action['domain'] = package_domain
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