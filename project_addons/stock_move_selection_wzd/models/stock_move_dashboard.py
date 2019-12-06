# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json

from odoo import models, api, _, fields

from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    @api.one
    def _kanban_dashboard_graph(self):
        self.kanban_dashboard_graph = json.dumps(self.get_bar_graph_datas())

    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    color = fields.Integer("Color Index", default=0)
    num_error_day = fields.Integer ("Dias de error", default = 3, help="Numero de días a mostrar con errores.")

    @api.multi
    def get_bar_graph_datas(self):

        state_pendientes = ('waiting', 'confirmed', 'assigned', 'partially_available')
        today = datetime.now().strftime(DEFAULT_SERVER_DATE_FORMAT)
        tomorrow = (datetime.now() + timedelta(days=1)).strftime(DEFAULT_SERVER_DATE_FORMAT)
        stock_move = self.env['stock.move']

        for type in self:
            comun_domain = [('picking_type_id', '=' , type.id)]
            wait_domain = [('state', 'in', state_pendientes)]

            later_domain = comun_domain + wait_domain + [('date_expected', '<=', today)]
            retrasados = stock_move.search_count(later_domain)

            pendientes_domain = comun_domain + wait_domain
            pendientes = stock_move.search_count(pendientes_domain)

            futuro_domain = comun_domain + wait_domain + [('date_expected', '>=', tomorrow)]
            futuro = stock_move.search_count(futuro_domain)

            hoy_domain = comun_domain + wait_domain + ['&', ('date_expected', '>=', today), ('date_expected', '<', tomorrow)]
            done_today = stock_move.search_count(hoy_domain)

            sql= "select count(*) from stock_move sm " \
                  "where sm.picking_type_id = {} and sm.state = 'done' and date > (current_date - interval '{} day') and " \
                  "(sm.product_uom_qty != sm.ordered_qty or sm.product_uom_qty != sm.product_uom_qty_orig or sm.sga_state in ('export_error', 'import_error'))".format(type.id, type.num_error_day)

            #sql = "select count(*) from stock_move sm where sm.picking_type_id = {} and sm.state = 'done'".format(type.id)
            print (sql)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            #print ('{}\n--------\n{}'.format(sql, res) )
            errores = res and res[0]['count'] or 0

            res = [{'values': [
                     {'label': 'Pendientes.', 'value': pendientes, 'type': 'past'},
                     {'label': 'Hoy', 'value': done_today, 'type': 'today'},
                     {'label': 'Futuro', 'value': futuro, 'type': 'future'},
                     {'label': 'Errores', 'value': errores, 'type': 'error'}],
            'title': 'Movimientos', 'key': 'Movimientos'}]
        return res
