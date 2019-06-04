# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import UserError


PICKING_TYPE_GROUP = [('incoming', 'Incoming'),
                      ('outgoing', 'Outgoing'),
                      ('picking', 'Picking'),
                      ('internal', 'Internal'),
                      ('location','Location'),
                      ('reposition','Reposition'),
                      ('other','Other')]


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    # @api.multi
    # def get_result_package_ids(self):
    #     self.ensure_one()
    #     packages = self.move_line_ids.mapped('result_package_id')
    #     self.current_package_list = [(6,0,packages.ids)]
    group_code = fields.Selection(PICKING_TYPE_GROUP, string="Code group")
    route_driver_id = fields.Many2one('res.partner', string='Route driver',
        help='Carrier driver for this batch picking.', domain="[('route_driver', '=', True)]")
    route_plate_id = fields.Many2one('delivery.plate', string='Route plate', help='Plate for this batch picking.')
    name = fields.Char(
        'Name',
        required=True, index=True,
        copy=False, unique=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'stock.batch.picking.lr'
        ),
    )
    carrier_id = fields.Many2one(
        'delivery.carrier', string='Delivery carrier', track_visibility='onchange',
        help='Delivery carrier for this batch picking.')
    carrier_partner_id = fields.Many2one(
        'res.partner', string='Carrier driver', track_visibility='onchange',
        help='Carrier driver for this batch picking.', domain="[('delivery_id', '=', carrier_id)]")
    has_packages = fields.Boolean(
        'Has Packages', compute='_compute_has_packages',
        help='Check the existence of destination packages on move lines')
    current_package_list = fields.One2many('stock.quant.package', "batch_picking_id", string="Packages")
    picking_type_id = fields.Many2one(
        string='Picking type',
        comodel_name='stock.picking.type',
    )
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

    #@api.model
    #def check_batch_location_ids(self):
    #    for batch in self:
    #        batch.current_location_id = batch.picking_type_id.default_location_src_id ## batch.picking_ids and batch.picking_ids[0].location_id or False
    #        batch.current_location_dest_id = batch.picking_type_id.default_location_src_id ## batch.picking_ids and batch.picking_ids[0].location_dest_id or False

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        for batch in self:
            batch.group_code = batch.picking_type_id.group_code

    @api.multi
    def write(self, vals):
        picking_type_id = vals.get('picking_type_id', False) ##and not vals.get('shipping_type')
        if picking_type_id:
            vals.update(group_code=self.env['stock.picking.type'].browse(picking_type_id).group_code)
        return super().write(vals)


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
        ctx.update(batch_picking_id = self.id)
        ctx.update(shipping_type= self.shipping_type)
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