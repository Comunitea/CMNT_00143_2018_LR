# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo import exceptions

class StockQuantPackage(models.Model):
    _inherit = 'stock.quant.package'

    state_progress = fields.Selection([('no_state', 'Sin Estado'),
                              ('preparation', 'Preparación'),
                              ('loading', 'Carga'),
                              ('internal', 'Almacén'),
                              ('customer', 'Cliente'),
                              ('supplier', 'Proveedor')],
                                      compute="compute_package_state_progress", store=True,
                                      help="Paquetes en preparación y no incluidos en una orden de carga",)

    package_to_load = fields.Boolean('Paquetes para cargar', store=False)
    partner_to_load = fields.Many2one('res.partner', string='Paquetes de ....', store=False)
    to_delivery = fields.Many2one('stock.batch.delivery', store=True)



    def get_picking_package_domain(self):
        domain = []
        if self.partner_id:
            domain += [('partner_id', '=', self.partner_id.id)]
        if self.delivery_route_path_id:
            domain += [('delivery_route_path_id', '=', self.delivery_route_path_id.id)]
        if self.shipping_type:
            domain += [('shipping_type', '=', self.shipping_type.id)]
        return domain

    @api.multi
    def confirm_package_in_delivery(self):
        ctx = self._context.copy()
        for package in self:
            moves_to_check = package.move_lines
            ctx.update(result_package_id=package.id)
            moves_to_check._assign_picking()

    @api.multi
    def show_package_move_ids(self):
        self.ensure_one()
        view = self.env.ref('stock_quant_package_wzd.sqp_form')
        return {
            'name': _('Detailed Operations'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.quant.package',
            'views': [(view.id, 'form')],
            'view_id': view.id,
            'target': 'new',
            'res_id': self.id,
            'context': dict(
            ),
        }


    @api.multi
    def add_package_to_batch_delivery(self):

        to_unlink = self.filtered(lambda x: x.batch_delivery_id)
        to_link = self.filtered(lambda x: not x.batch_delivery_id and x.to_delivery != False)
        for package_id in to_unlink:
            package_id.assign_delivery(False)
        if to_link:
            to_delivery_ctx = self._context.get('to_delivery', False)
            to_delivery_ctx_id = self.env['stock.batch.picking'].browse(to_delivery_ctx)
            for package_id in to_link:
                to_delivery = package_id.to_delivery or to_delivery_ctx_id or False
                if to_delivery:
                    package_id.assign_delivery(to_delivery)
                    package_id.write({'to_delivery': False})

    @api.multi
    def assign_delivery(self, delivery_id):
        real = False
        if delivery_id:
            self.write({'batch_delivery_id': delivery_id.id})
            if real:
                moves_in_self = self.mapped('move_line_ids').mapped('move_id')
                picks_in_self = moves_in_self.mapped('picking_id')
                new_picks = picks_in_self.split_if_package(delivery_id)
                picks_in_self._assign_picking_batch()
        else:
            self.action_cancel_delivery_batch_assigment()
            ## self.write({'batch_delivery_id': False})
            self.picking_ids.write({'batch_delivery_id': False})


    @api.model
    def search(self, args1, offset=0, limit=None, order=None, count=False):
        def get_move_domain():
            move_domain = [('location_id.preparation_location', '=', True),
                       ('state', 'in', ('assigned', 'partially_available')),
                       ('result_package_id', '!=', False)]
            return move_domain

        if self._context.get('package_to_load', False):
            domain = get_move_domain()
            sqp_ids = self.env['stock.move.line'].search_read(domain, ['result_package_id'])
            if sqp_ids:
                args1 += [('id', 'in', [sqp['result_package_id'][0] for sqp in sqp_ids])]
        if self._context.get('partner_to_load', False):
            index = 0
            for arg in args1:
                if arg[0] == 'partner_to_load':
                    domain = get_move_domain() + [('partner_id', '=', arg[2])]
                    sqp_ids = self.env['stock.move.line'].search_read(domain, ['result_package_id'])
                    if sqp_ids:
                        arg = ('id', 'in', [sqp['result_package_id'][0] for sqp in sqp_ids])
                        args1[index] = arg
                    else:
                        args1[index] = ('id', '=', False)
                index += 1
        return super().search(args=args1, offset=offset, limit=limit, order=order, count=count)

    @api.multi
    @api.depends('move_line_ids.state', 'move_line_ids')
    def compute_package_state_progress(self):
        for package in self:
            move_line_ids = package.move_line_ids
            if all(x.state == 'done' for x in move_line_ids):
                ##Miro el estado por la ubicación
                if package.location_id and package.location_id.usage=='customer':
                    package.state_progress = 'customer'
                    continue
                if package.location_id and package.location_id.usage=='supplier':
                    package.state_progress = 'supplier'
                    continue
                if package.location_id and package.location_id.usage=='internal':
                    if package.batch_delivery_id:
                        package.state_progress = 'loading'
                        continue
                    package.state_progress = 'internal'
                    continue
            elif move_line_ids and all(x.location_id.preparation_location for x in move_line_ids):
                if package.batch_delivery_id:
                    package.state_progress = 'loading'
                    continue
                package.state_progress = 'preparation'
                continue
            package.state_progress = 'no_state'