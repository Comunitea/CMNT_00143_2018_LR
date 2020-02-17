# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError,ValidationError
from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE, HELP_SHIPPING_TYPE


class StockBatchDelivery(models.Model):

    _inherit = 'stock.batch.delivery'

    @api.multi
    def action_confirm(self):
        self.write({'state': 'ready'})
        ctx = self._context.copy()
        ##AQUI LO QUE VOY A HACER ES:
        ## SEPARAR LOS ALBARANES Y DEJAR LOS MOVIMIENTOS
        for delivery_id in self:

                # 1º DIVIDO LOS MOVIMIENTOS QUE NO TESTEN COMPLETOS EN UN PAQUETE Y NO VAYAN EN LA ORDEN
                # 2º SPLIT DE LOS PICKINGS SI HAY MERCANCÍA QUE NO ESTÁ EN LOS PAQUETES
                # 3º PONGO LA CANTIDAD COMO HECHA EN LOS PICKINGS ASOCIADOS A LOS PAQUETES
                # 5º CREO LOS ALBARANES DE CLIENTE
                # y asigno orden para los clientes
                # 6º AL MARCAR LA ORDEN COMO HECHA
                    # VALIDO LAS AGRUPACIONES. AL VALIDAR LAS AGRUPACIONES, SE VALIDAN LOS ALBARANES DE CLIENTE

                # 1º DIVIDO LOS MOVIMIENTOS QUE NO TESTEN COMPLETOS EN UN PAQUETE Y NO VAYAN EN LA ORDEN
                # TODO

                # 2º SPLIT DE LOS PICKINGS SI HAY MERCANCÍA QUE NO ESTÁ EN LOS PAQUETES

                picking_ids = delivery_id.package_ids.mapped('move_line_ids').mapped('picking_id')
                moves_to_split = picking_ids.mapped('move_line_ids').filtered(lambda x: x.result_package_id.batch_delivery_id == False).mapped('move_id')
                moves_in_delivery = picking_ids.mapped('move_line_ids').filtered(lambda x: x.result_package_id.batch_delivery_id).mapped('move_id')
                if moves_to_split:
                    moves_to_split.mapped('picking_id').split_if_package(moves_to_split, delivery_id)

                # 3º PONGO LA CANTIDAD COMO HECHA EN LOS PICKINGS ASOCIADOS A LOS PAQUETES
                ## TODO REVISAR PARA NUMEROS DE SERIE
                for move_line in delivery_id.package_ids.mapped('move_line_ids'):
                    move_line.qty_done = move_line.product_uom_qty

                # 4º CREO LOS ALBARANES DE CLIENTE
                ctx.update(default_batch_picking_id=self.id)

                batch_ids = moves_in_delivery.mapped('picking_id').with_context(ctx)._assign_picking_batch()

                # 5º ESCRIBO LA ORDEN DE ENTREGA EN LOS ALBARANES
                ## Lo hago en el split_if_package ????

                batch_ids.write({'state': 'assigned', 'batch_delivery_id': delivery_id.id})
                delivery_id.update_partner_order()

    @api.multi
    def add_more_packages(self):

        self.ensure_one()
        action = self.env.ref(
            'stock_quant_package_wzd.action_sqp_tree').read()[0]
        domain = ['|', ('batch_delivery_id', '=', self.id), ('batch_delivery_id', '=', False), ('state_progress', '=', 'preparation')]
        if self.delivery_route_path_ids:
            domain  += [('delivery_route_path_id', 'in', self.delivery_route_path_ids.ids)]
        if self.shipping_type:
            domain += [('shipping_type', '=', self.shipping_type)]
        action['domain'] = domain
        self.env['stock.quant.package'].search(domain).write({'to_delivery': self.id})
        ctx = self._context.copy()
        ctx.update(eval(action['context']))
        ctx.update(to_delivery=self.id)
        action['name'] = "Mas paquetes a la orden : {}".format(self.name)
        action['display_name'] = "Orden: {}".format(self.name)
        action['context'] = ctx
        return action

    @api.multi
    def action_view_stock_package(self):
        action = super().action_view_stock_package()
        view_tree = self.env.ref('stock_quant_package_wzd.sqp_tree')
        view_kanban = self.env.ref('stock.view_quant_package_kanban')
        action['views'] = {(view_tree.id, 'tree'), (view_kanban.id, 'kanban')}
        action['view_id'] = view_tree.id
        return action