# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE

class ConfigBatchDeliveryWzd(models.TransientModel):

    _name = 'config.batch.delivery.wzd'

    stock_batch_delivery_id = fields.Many2one('stock.batch.delivery', readonly=True, string='Orden de carga')
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta asignada")
    info_route_str = fields.Char('Info de entrega', compute='get_info_route')
    urgent = fields.Boolean('Urgente')
    date_expected = fields.Date('Fecha prevista')
    picker_id = fields.Many2one('res.users', 'Operario')
    carrier_id = fields.Many2one("delivery.carrier", string="Agencia")
    notes = fields.Text('Notas', help='free form remarks')
    driver_id = fields.Many2one('res.partner', string='Conductor',
                                help='Carrier driver for this batch picking.',
                                domain="[('route_driver', '=', True)]")
    plate_id = fields.Many2one('delivery.plate', string='Matrícula', help='Plate for this batch picking.')

    @api.model
    def default_get(self, fields):
        defaults = super().default_get(fields)

        new_id = self._context.get('active_id', False)
        if new_id:
            sbd_id = self.env['stock.batch.delivery'].browse(new_id)
            defaults.update(
                {
                    'stock_batch_delivery_id': new_id,
                    'shipping_type': sbd_id.shipping_type,
                    'delivery_route_path_id': sbd_id.delivery_route_path_id.id,
                    'date_expected': sbd_id.date_expected,
                    'picker_id': sbd_id.picker_id.id,
                    'carrier_id': sbd_id.carrier_id.id,
                    'driver_id': sbd_id.driver_id.id,
                    'plate_id': sbd_id.plate_id.id,
                    'notes': sbd_id.notes,
                }
            )
        return defaults

    @api.multi
    def action_apply_changes(self):
        vals = {
                    'shipping_type': self.shipping_type,
                    'delivery_route_path_id': self.delivery_route_path_id.id,
                    'date_expected': self.date_expected,
                    'picker_id': self.picker_id.id,
                    'carrier_id': self.carrier_id.id,
                    'driver_id': self.driver_id.id,
                    'plate_id': self.plate_id.id,
                    #'notes': self.notes,
                }
        self.stock_batch_delivery_id.write(vals)
        self.stock_batch_delivery_id.batch_ids.write(vals)
        return








