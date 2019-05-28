# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


import json
from datetime import datetime, timedelta
from babel.dates import format_datetime, format_date

from odoo import models, api, _, fields
from odoo.release import version
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools.misc import formatLang


from .stock_picking import PICKING_TYPE_GROUP

class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'


    @api.one
    def _kanban_dashboard_graph(self):
        self.kanban_dashboard_graph = json.dumps(self.get_bar_graph_datas())

    kanban_dashboard_graph = fields.Text(compute='_kanban_dashboard_graph')
    color = fields.Integer("Color Index", default=0)
    num_error_day = fields.Integer ("Numero días a mostrar con errores", default = 3)

    @api.multi
    def get_bar_graph_datas(self):

        state_pendientes = ('waiting', 'confirmed', 'assigned', 'partially_available')
        for type in self:
            ## sql generica para el picking_type
            sql1 = "select count(*) from stock_move where company_id = {} and picking_type_id = {}".format(self.env.user.company_id.id, type.id)
            ##RETRASADOS
            sql = "{} and state in {} and date(date_expected) < current_date".format(sql1, state_pendientes)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            retrasados = res and res[0] or 0

            ##HOY
            sql = "{} and state in {} and date(date_expected) = current_date ".format(sql1, state_pendientes)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            hoy = res and res[0] or 0

            ##Retornos
            sql = "{} and state in {} and origin_returned_move_id isnull".format(sql1, state_pendientes)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            retornos = res and res[0] or 0

            ## Realizados Hoy
            sql = "{} and state = 'done' and  date(date_expected) = current_date".format(sql1)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            done_today = res and res[0] or 0

            sql = "{} and state in {} and  date(date_expected) > current_date".format(sql1,state_pendientes)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            futuro = res and res[0] or 0

            sql = "select count(sm.id) from stock_move sm where (select sum(qty_done) from stock_move_line sml where " \
                  "sm.company_id= {} and " \
                  "sm.picking_type_id = {} and  " \
                  "sml.move_id = sm.id) != sm.ordered_qty " \
                  "and state = 'done' and " \
                  "date > current_date - interval '{} day'".format(self.env.user.company_id.id, type.id, type.num_error_day)
            self.env.cr.execute(sql)
            res = self.env.cr.dictfetchall()
            errores = res and res[0] or 0

            res = [{'values': [
                     {'label': 'Retrasados.', 'value': retrasados['count'] + hoy['count'], 'type': 'past'},
                     {'label': 'Hoy', 'value': done_today['count'], 'type': 'today'},
                     #{'label': 'Retornos', 'value': retornos['count'], 'type': 'return'},
                     {'label': 'Futuro', 'value': futuro['count'], 'type': 'future'},
                     {'label': 'Errores', 'value': errores['count'], 'type': 'error'}],
            'title': 'Movimientos', 'key': 'Movimientos'}]
            print (res)
        return res
