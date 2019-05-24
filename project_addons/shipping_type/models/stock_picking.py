# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .res_partner import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE


class StockPickintType(models.Model):
    _inherit = 'stock.picking.type'

    shipping_type = fields.Boolean('Agrupa por tipo de envío')
    delivery_route_path_id = fields.Boolean('Agrupa por ruta de transporte')
    carrier_id = fields.Boolean('Agrupa por forma de envío')
    campaign_id = fields.Boolean('Agrupa por campaña')


class StockBatchPicking(models.Model):
    _inherit = 'stock.batch.picking'

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE, help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    urgent = fields.Boolean("Urgent", help='Plus 3,20%')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.onchange('carrier_id')
    def onchange_carrier_id(self):
        for batch in self:
            batch.picking_ids.write({'carrier_id': batch.carrier_id.id})

    @api.onchange('shipping_type')
    def onchange_shipping_type(self):
        for batch in self:
            batch.picking_ids.write({'shipping_type': batch.shipping_type})

    @api.onchange('delivery_route_path_id')
    def onchange_delivery_route_path_id(self):
        for batch in self:
            batch.picking_ids.write({'delivery_route_path_id': batch.delivery_route_path_id.id})

    @api.onchange('urgent')
    def onchange_urgent(self):
        for batch in self:
            batch.picking_ids.write({'urgent': batch.urgent})


class StockPicking(models.Model):
    _inherit = "stock.picking"

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE, help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    urgent = fields.Boolean("Urgent", help='Plus 3,20%')
    campaign_id = fields.Many2one('campaign', 'Campaign')

    @api.onchange('shipping_type')
    def onchange_shipping_type(self):
        for pick in self:
            pick.move_line.write({'shipping_type': pick.shipping_type})

    @api.onchange('delivery_route_path_id')
    def onchange_delivery_route_path_id(self):
        for pick in self:
            pick.move_line.write({'delivery_route_path_id': pick.delivery_route_path_id.id})

    @api.onchange('urgent')
    def onchange_urgent(self):
        for pick in self:
            pick.move_line.write({'urgent': pick.urgent})

    def get_new_vals(self):
        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'urgent': self.urgent,
                'carrier_id': self.carrier_id.id
                }
        return vals

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    urgent = fields.Boolean("Urgent", help='Plus 3,20%')
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


class StockMove(models.Model):

    _inherit = "stock.move"

    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE, help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    urgent = fields.Boolean("Urgent", help='Plus 3,20%')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    campaign_id = fields.Many2one('campaign', 'Campaign')

    def _get_new_picking_domain(self):
        domain = super()._get_new_picking_domain()
        if self.picking_type_id:
            if self.picking_type_id.shipping_type:
                domain += [('shipping_type', '=', self.shipping_type)]
            if self.picking_type_id.delivery_route_path_id:
                domain += [('delivery_route_path_id', '=', self.delivery_route_path_id.id)]
            if self.picking_type_id.carrier_id:
                domain += [('carrier_id', '=', self.carrier_id.id)]
            if self.picking_type_id.campaign_id:
                domain += [('campaign_id', '=', self.campaign_id.id)]
        return domain

    def get_new_vals(self):
        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'urgent': self.urgent,
                'carrier_id': self.carrier_id.id,
                'campaign_id': self.campaign_id and self.campaign_id.id
                }
        return vals

    def _get_new_picking_values(self):
        res = super()._get_new_picking_values()
        res.update(self.get_new_vals())
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
