# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from odoo.exceptions import ValidationError

class StockMovePackListWzd(models.TransientModel):
    _name = 'stock.move.pack.list.wzd'

    wzd_id = fields.Many2many('stock.move.pack.wzd')
    selected = fields.Boolean('Seleccionado')
    package_id = fields.Many2one('stock.quant.package', string='Paquete',readonly="1")
    move_ids = fields.Many2many('stock.move', string='Movimientos',readonly="1")
    partner_id = fields.Many2one(related='package_id.partner_id',readonly="1")
    info_route_str = fields.Char(related='package_id.info_route_str', string='Info ruta',readonly="1")

    @api.multi
    def action_assign_this_package(self):
        package = self.package_id
        for move in self.wzd_id.move_ids:
            move.assign_package(package)
        self.wzd_id.autorefresh()

class StockMovePackWzd(models.TransientModel):
    """Wzd to select pack for pack move
    """

    _name = 'stock.move.pack.wzd'
    _description = 'Asistente para empaquetar'

    partner_id = fields.Many2one('res.partner', 'Cliente/Proveedor')
    move_ids = fields.Many2many('stock.move', string='Para empaquetar')
    move_line_ids = fields.Many2many('stock.move.line', string='Para empaquetar')
    shipping_type = fields.Selection(SHIPPING_TYPE_SEL, default=DEFAULT_SHIPPING_TYPE, string=STRING_SHIPPING_TYPE,
                                     help=HELP_SHIPPING_TYPE)
    delivery_route_path_id = fields.Many2one('delivery.route.path', string="Route path")
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    list_packages_ids = fields.Many2many('stock.move.pack.list.wzd', string='Paquetes')

    def _prepare_package(self, pack):
        return {#'partner_id': pack.partner_id and pack.partner_id.id,
                'package_id': pack.id,
                'move_ids': [(6, 0, pack.move_line_ids.mapped('move_id').ids)],
                'info_route_str': pack.info_route_str}

    @api.model
    def default_get(self, fields):
        return super().default_get(fields)

    def action_unassign_package(self):
        self.move_ids.unpack()

    def action_assign_package(self):
        ##TODO DELETE FUNCTION
        package = self.list_packages_ids.filtered(lambda x: x.selected).package_id
        for move in self.move_ids:
            move.assign_package(package)

    def action_assign_new_package(self):
        new_package_vals = {'partner_id': self.partner_id.id,
                            'shipping_type': self.shipping_type,
                            'delivery_route_path_id': self.delivery_route_path_id.id,
                            'carrier_id': self.carrier_id.id}
        new_pack = self.env['stock.quant.package'].create(new_package_vals)
        for move in self.move_ids:
            move.assign_package(new_pack)
        return True

    @api.multi
    def action_assign_route(self):
        vals = {'shipping_type': self.shipping_type,
                'delivery_route_path_id': self.delivery_route_path_id.id,
                'carrier_id': self.carrier_id.id}
        self.packages_ids.write(vals)
        return self.autorefresh()

    def autorefresh(self):
        action = self.env.ref('stock_move_selection_wzd.view_stock_move_pack_wzd_act_window').read()[0]
        action['res_id'] = self.id
        return action

    def create_from_moves(self, moves):

        move_line_ids = moves.mapped('move_line_ids')
        not_moves = moves.filtered(lambda x: x.picking_type_id.code != 'outgoing')
        #if not_moves:
        #    raise ValidationError(_('No hay movimientos de salida seleccionados'))
        if moves.filtered(lambda x: x.batch_delivery_id):
            raise ValidationError(_('Algunos movimientos ya tienen orden de carga seleccionada'))
        if moves.filtered(lambda x: x.state not in ('partially_available', 'assigned')):
            raise ValidationError(_("Tienes movimientos en estado distinto a 'Reservado'"))
        if moves.filtered(lambda x: x.result_package_ids):
            raise ValidationError(_("Tienes movimientos ya empaquetados"))

        if len(moves.mapped('partner_id')) != 1 and moves.mapped('picking_type_id').mapped('code') == 'outgoing':
            raise ValidationError(_("Tienes movimientos de distinto cliente"))

        vals = {}
        package_domain = [('state', 'in', ('assigned', 'partially_available')),
                          ('move_id.partner_id', '=', moves[0].partner_id.id)]

        if len(dict.fromkeys(moves.mapped('shipping_type')).keys()) == 1:
            vals.update(shipping_type=moves[0].shipping_type)
            package_domain += [('shipping_type', '=', moves[0].shipping_type)]
        if len(moves.mapped('delivery_route_path_id')) == 1:
            vals.update(delivery_route_path_id=moves[0].delivery_route_path_id.id)
            package_domain += [('delivery_route_path_id', '=', moves[0].delivery_route_path_id.id)]
        #if len(moves.mapped('picking_id').mapped('carrier_id')) == 1:
        #    vals.update(carrier_id=moves[0].picking_id.carrier_id.id)
        #    package_domain += [('carrier_id', '=', moves[0].picking_id.carrier_id.id)]
        if len(moves.mapped('partner_id')) == 1:
            vals.update(partner_id=moves[0].partner_id.id)
            package_domain += [('partner_id', '=', moves[0].partner_id.id)]
        ##Paquetes disponibles no enviados
        move_lines = self.env['stock.move.line'].search(package_domain)
        package_available = move_lines.mapped('result_package_id')
        ##Estudiar esto. No hay ningún campo que marque el paquete como vacío. Si busco paquetes vacíos la busqueda puede ser muyyyy lenta
        vals.update(list_packages_ids=[(0, 0, self._prepare_package(x)) for x in package_available])
        vals.update(move_line_ids=[(6, 0, move_line_ids.ids)])
        vals.update(move_ids=[(6, 0, moves.ids)])
        return self.create(vals)