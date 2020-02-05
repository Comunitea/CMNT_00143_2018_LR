# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _
from .info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockQuantPackage(models.Model):

    _inherit = ['stock.quant.package', 'info.route.mixin']
    _name = 'stock.quant.package'

    @api.multi
    def _count_move_line_ids(self):
        for pack in self:
            pack.count_move_line = len(pack.move_line_ids)

    count_move_line = fields.Integer(compute=_count_move_line_ids)
    picking_ids = fields.One2many('stock.picking', compute='get_stock_pickings')
    payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago')
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")

    @api.depends('quant_ids.package_id', 'quant_ids.location_id', 'quant_ids.company_id', 'quant_ids.owner_id')
    def _compute_package_info(self):
        #Por rendimeinto no heredo
        super()._compute_package_info()
        for package in self.filtered(lambda x: not x.quant_ids):
            location_ids = package.move_line_ids.mapped('location_id')
            if len(location_ids) == 1:
                package.location_id = location_ids[0]

    def _compute_current_picking_info(self):
        return super()._compute_current_picking_info()
        """ When a package is in displayed in picking, it gets the picking id trough the context, and this function
        populates the different fields used when we move entire packages in pickings.
        """
        ## esta función puede fallar ahora, ya que no todos los movimientos tienenq que porque ser del mismo albarán

        for package in self:
            picking_id = self.env.context.get('picking_id')
            if not picking_id:
                package.current_picking_move_line_ids = False
                package.current_picking_id = False
                package.is_processed = False
                package.current_source_location_id = False
                package.current_destination_location_id = False
                continue

            package.current_picking_move_line_ids = package.move_line_ids.filtered(lambda ml: ml.picking_id.id == picking_id)
            package.current_picking_id = True
            package.current_source_location_id = package.current_picking_move_line_ids[:1].location_id
            package.current_destination_location_id = package.current_picking_move_line_ids[:1].location_dest_id
            package.is_processed = not bool(package.current_picking_move_line_ids.filtered(lambda ml: ml.qty_done < ml.product_uom_qty))

        return True

    @api.multi
    def set_route_fields(self):
        for pack in self:
            pack.check_allow_change_route_fields()
            moves = pack.move_line_ids.mapped('move_id')
            vals = {}
            vals.update({'shipping_type': pack.shipping_type,
                         'delivery_route_path_id': pack.delivery_route_path_id.id,
                         'carrier_id': pack.carrier_id.id})
            moves.write(vals)

    @api.multi
    def get_stock_pickings(self):
        return

    def propagate_route_vals(self, vals):
        return True

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        r_vals = ['payment_term_id', 'shipping_type', 'delivery_route_path_id', 'carrier_id', 'campaign_id']
        vals  = list(set([x for x in vals.keys()]) & set(r_vals))
        if not vals:
            return res
        for pack in self:
            if not self._context.get('from_parent', False):
                ## Si no viene de una orden de carga, entonces ....
                picking_ids = pack.move_line_ids.mapped('picking_id')

                if any(x in ('done', 'cancel') for x in pack.move_line_ids.mapped('state')):
                    raise ValidationError (_('No puedes hacer cambiar estos valores en movimientos ya realizados'))
                if any(x.batch_picking_id for x in picking_ids):
                    raise ValidationError(_('No puedes hacer cambiar estos valores en movimientos ya alabaranados'))

            pack.move_line_ids.mapped('move_id').write(pack.update_info_route_vals())

        return res








