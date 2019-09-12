# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE


class StockMoveLine(models.Model):

    _inherit = ['stock.move.line', 'info.route.mixin']
    _name = 'stock.move.line'

    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')


    @api.model
    def create(self, vals):
        return super().create(vals)


    @api.multi
    def write(self, vals):
        return super().write(vals)
        child_vals = self.get_write_route_vals(vals)
        if child_vals and self.mapped('result_package_id') and not self._context.get('force_route_vals', False):
            raise ValidationError('No puedes cambiar la información de ruta de un movimiento empaquetado. Cambialo desde el paquete o desempaquetado')
        return super().write(vals)

    def update_to_new_package(self, new_package_ids):
        ## revisar esto
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
        return super()._get_new_picking_domain()

    def get_new_vals(self):
        vals = self.update_info_route_vals()
        return vals

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        if self.picking_type_id.code == 'outgoing':
            res.update(self.get_new_vals())
        return res

    def _prepare_procurement_values(self):
        res = super()._prepare_procurement_values()
        res.update(self.update_info_route_vals())
        return res

    def _prepare_move_line_vals(self, quantity=None, reserved_quant=None):
        res = super()._prepare_move_line_vals(quantity=quantity, reserved_quant=reserved_quant)
        res.update(self.update_info_route_vals())
        return res

    def _prepare_extra_move_vals(self, qty):
        res = super()._prepare_extra_move_vals(qty=qty)
        res.update(self.update_info_route_vals())
        return res

    def _prepare_move_split_vals(self, qty):
        res = super()._prepare_move_split_vals(qty=qty)
        res.update(self.update_info_route_vals())
        return res

    def propagate_route_vals(self, vals):

        child_vals = self.get_write_route_vals(vals)
        if child_vals:
            if self.mapped('move_line_ids').mapped('result_package_id') and not self._context.get('force_route_vals', False):
                raise ValidationError('Hay movimientos con paquetes. Debes cambiar los datos de envío en los paquetes')
            self.mapped('move_line_ids').write(child_vals)
        return

    @api.multi
    def write(self, vals):
        if self._context.get('no_propagate_route_vals', True):
            self.propagate_route_vals(vals)
        super().write(vals)

