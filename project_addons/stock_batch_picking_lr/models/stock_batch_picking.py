# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from odoo.exceptions import UserError

from pprint import pprint

class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    carrier_id = fields.Many2one(
        'delivery.carrier', string='Delivery carrier', track_visibility='onchange',
        help='Delivery carrier for this batch picking.')
    carrier_partner_id = fields.Many2one(
        'res.partner', string='Carrier driver', track_visibility='onchange',
        help='Carrier driver for this batch picking.', domain="[('delivery_id', '=', carrier_id)]")
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
    packages_added_manually = fields.One2many('stock.quant.package', 'stock_batch_id', 'Quants')

    @api.multi
    def action_see_packages(self):
        pprint("MECAGOENDIOS_______________________________________________________________")
        self.ensure_one()
        action = self.env.ref('stock.action_package_view').read()[0]
        packages = self.picking_ids.mapped('move_line_ids').mapped('result_package_id')
        action['domain'] = [('id', 'in', packages.ids)]
        action['context'] = {'picking_id': self.id}
        return action

    @api.multi
    def write(self, vals):
        self._check_if_adding_packages(vals)
        return super(StockBatchPicking, self).write(vals=vals)

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
    
    @api.model
    def _check_if_adding_packages(self, vals):
        if vals.get('packages_added_manually'):

            for package_action in vals.get('packages_added_manually'):
                
                if package_action[0] == 3:
                    self._delete_package_from_picking(package_action[1])                
                
                elif package_action[0] == 4:

                    self._add_package_to_picking(package_action[1])
                           
                elif package_action[0] == 6:
                    for package_id in package_action[2]:
                        self._add_package_to_picking(package_id)
    
    @api.model
    def _delete_package_from_picking(self, package_id):
        move_lines = self.env['stock.quant.package'].browse(package_id).move_line_ids
        for line in move_lines:
            self.env['stock.move.line'].browse(line.id).write({
                'picking_id': None
            })
            self.env['stock.move'].browse(line.move_id.id).write({
                'picking_id': None
            })  
    
    @api.model
    def _add_package_to_picking(self, package_id):
        dest_partner = self.env['stock.quant.package'].browse(package_id).dest_partner_id
        picking_partner_ids = self.picking_ids.mapped('partner_id')

        if dest_partner in picking_partner_ids:
            picking_id = self.picking_ids.search([('partner_id', '=', dest_partner.id)], limit=1)
            move_lines = self.env['stock.quant.package'].browse(package_id).move_line_ids
            for line in move_lines:
                self.env['stock.move.line'].browse(line.id).write({
                    'picking_id': picking_id.id
                })
                self.env['stock.move'].browse(line.move_id.id).write({
                    'picking_id': picking_id.id
                })
                self.env['stock.move'].browse(line.id).action_force_assign_picking()
        else:
            data = {
                'location_id' : self._get_default_location_id(),
                'location_dest_id': self._get_default_location_dest_id(),
                'picking_type_id': self._get_default_outgoing_warehouse(),
                'batch_picking_id': self.id
            }      
            picking_id = self.env['stock.picking'].create(data)
            self.env['stock.picking'].browse(picking_id.id).write({'partner_id': dest_partner.id})

            obj = self.env['stock.picking'].browse(picking_id.id)

            pprint(obj)

            pprint(obj.partner_id)

            #No me guarda el valor de partner o lo sobreescribe después. Revisar

            move_lines = self.env['stock.quant.package'].browse(package_id).move_line_ids
            for line in move_lines:
                self.env['stock.move.line'].browse(line.id).write({
                    'picking_id': picking_id.id
                })
                self.env['stock.move'].browse(line.move_id.id).write({
                    'picking_id': picking_id.id
                })
                self.env['stock.move'].browse(line.move_id.id).action_force_assign_picking()

    @api.model
    def _get_default_outgoing_warehouse(self):
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_obj = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)])

        picking_type_obj = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse_obj.id), ('active', '=', True), ('code', '=', 'outgoing')])

        return picking_type_obj.id
    
    @api.model
    def _get_default_location_id(self):
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_obj = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)])

        picking_type_obj = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse_obj.id), ('active', '=', True), ('code', '=', 'outgoing')])

        return picking_type_obj.default_location_src_id.id
    
    @api.model
    def _get_default_location_dest_id(self):
        location_obj = self.env['stock.location'].search([('usage', '=', 'customer'), ('active', '=', True)])
        user_obj = self.env['res.users'].browse(self._uid)
        warehouse_obj = self.env['stock.warehouse'].search([('company_id', '=', user_obj.company_id.id)])

        picking_type_obj = self.env['stock.picking.type'].search([('warehouse_id', '=', warehouse_obj.id), ('active', '=', True), ('code', '=', 'outgoing')])

        return picking_type_obj.default_location_dest_id.id or location_obj.id

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