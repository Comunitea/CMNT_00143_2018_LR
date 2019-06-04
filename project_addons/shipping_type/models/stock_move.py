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
            #Hace falta escribir en el move_line_id
            #ml.move_id and ml.move_id.write(vals)

    @api.multi
    def write(self, vals):
        if 'result_package_id' in vals:
            vals.update(self.write_move_vals_in_package(vals['result_package_id']))
        return super().write(vals)

    def write_move_vals_in_package (self, package_id=False):
        pack = self.env['stock.quant.package'].browse(package_id)
        vals_0 = self and self[0].update_info_route_vals()

        pack.write(vals_0)
        return vals_0




class StockMove(models.Model):
    _inherit = ['stock.move', 'info.route.mixin']
    _name = 'stock.move'
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        if self.picking_type_id.code == 'outgoing':
            if self.shipping_type:
                domain += [('shipping_type', '=', self.shipping_type)]
            if self.delivery_route_path_id:
                domain += [('delivery_route_path_id', '=', self.delivery_route_path_id.id)]
            if self.carrier_id:
                domain += [('carrier_id', '=', self.carrier_id.id)]
            if self.campaign_id and False:
                domain += [('campaign_id', '=', self.campaign_id.id)]
            domain += [('urgent', '=', self.urgent)]
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

    @api.multi
    def write(self, vals):
        child_vals = self.get_child_vals(vals)
        if child_vals:
            ctx = self._context.copy()
            ctx.update(write_from_move=True)
            if self.mapped('move_line_ids').mapped('result_package_id') and not self._context.get('write_from_package') and not self._context.get('write_from_pick'):
                raise ValidationError('Hay movimientos con paquetes. Debes cambiar los datos de envío en los paquetes')
            if self.mapped('picking_id') and not self._context.get('write_from_pick') :
                raise ValidationError('Hay movimientos con albaranes. Debes cambiar los datos de envío en los albaranes')
            self.mapped('move_line_ids').write(child_vals)
        super().write(vals)



