# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .res_partner import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE


class StockMoveLine(models.Model):

    _inherit = ['stock.move.line', 'info.route.mixin']
    _name = 'stock.move.line'
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')

    @api.model
    def create(self, vals):
        print (vals)
        ml = super().create(vals)
        if ml.picking_id:
            vals = ml.picking_id.get_new_vals()
            ml.write(vals)

    @api.multi
    def write(self, vals):
        if self._context.get('write_from_move') and 'result_package_id' in vals:
            vals.pop('result_package_id')
        if False and 'result_package_id' in vals and not self._context.get('write_from_package') and not self._context.get('write_from_pick') :
            if self.mapped('picking_id'):
                raise ValidationError('No puedes cambiar el empaquetado de un movimiento con albarán')
        return super().write(vals)

    def update_to_new_package(self, new_package_ids):
        create = True
        for pack in new_package_ids:
            ok = pack.update_info_route_vals() == self.update_info_route_vals()
            if ok:
                self.move_id.write({'result_package_id': pack.id})
                create = False
                break
        if create:
            vals_0 = self.update_info_route_vals()
            new_result_package_id = pack.create(vals_0)
            self.move_id.write({'result_package_id': new_result_package_id.id})
            new_package_ids += new_result_package_id
        return new_package_ids


class StockMove(models.Model):
    _inherit = ['stock.move', 'info.route.mixin']
    _name = 'stock.move'
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        if self.picking_type_id.code == 'outgoing':
            if self.picking_type_id.bool_shipping_type and self.shipping_type :
                domain += [('shipping_type', '=', self.shipping_type)]
            if self.picking_type_id.bool_delivery_route_path_id and self.delivery_route_path_id:
                domain += [('delivery_route_path_id', '=', self.delivery_route_path_id.id)]
            if self.picking_type_id.bool_carrier_id and self.carrier_id:
                domain += [('carrier_id', '=', self.carrier_id.id)]
            if self.picking_type_id.bool_campaign_id and self.campaign_id:
                domain += [('campaign_id', '=', self.campaign_id.id)]
            #domain += [('urgent', '=', self.urgent)]
        print('Get new picking domain {}'.format(domain))
        return domain

    def get_new_vals(self):
        vals = self.update_info_route_vals()
        return vals

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        res.update(self.get_new_vals())
        print ('Valores para el nuevo pick: {}'.format(res))
        return res

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update(self.get_new_vals())
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        res.update(self.get_new_vals())
        return res

    def _prepare_extra_move_vals(self, qty):
        res = super()._prepare_extra_move_vals(qty=qty)
        res.update(self.get_new_vals())
        return res

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty=qty)
        res.update(self.get_new_vals())
        return res

    def propagate_route_vals(self, vals):
        child_vals = self.get_child_vals(vals)
        if child_vals:
            ctx = self._context.copy()
            ctx.update(write_from_move=True)
            if self.mapped('move_line_ids').mapped('result_package_id') and not self._context.get('write_from_package'):
                raise ValidationError('Hay movimientos con paquetes. Debes cambiar los datos de envío en los paquetes')

            if self.mapped('picking_id') and not self._context.get('write_from_pick'):
                raise ValidationError(
                    'Hay movimientos con albaranes. Debes cambiar los datos de envío en los albaranes')
            self.mapped('move_line_ids').write(child_vals)


        return


        ctx = self._context.copy()
        ctx.update(write_from_picking=True)
        move_vals = {}
        if 'picking_id' in vals:
            picking_id = vals['picking_id']
            move_vals.update({'picking_id': vals['picking_id']})
            pick = self.env['stock.picking'].browse(picking_id)
            if pick:
                child_vals = pick.get_child_vals(vals)
                if child_vals:
                    move_vals.update(child_vals)

            ctx = self._context.copy()
            ctx.update(write_from_package=True)
            self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(move_vals)
        else:
            child_vals = self.get_child_vals(vals)
            if child_vals:
                if self.mapped('picking_id') and not self._context.get('write_from_pick', False):
                    raise ValidationError('No puedes cambiar estos valores en el paquete si ya está en un albarán')
                ctx = self._context.copy()
                ctx.update(write_from_package=True)
                move_vals.update(child_vals)
                self.mapped('move_line_ids').mapped('move_id').with_context(ctx).write(move_vals)


    @api.multi
    def write(self, vals):
        if self._context.get('no_propagate_route_vals', True):
            self.propagate_route_vals(vals)
        super().write(vals)
