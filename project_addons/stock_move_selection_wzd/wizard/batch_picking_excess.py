# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE,HELP_SHIPPING_TYPE
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT

class BatchExcessLine(models.TransientModel):
    _name = 'batch.excess.line'

    wzd_id = fields.Many2one('batch.excess.wzd')
    batch_id = fields.Many2one('stock.batch.picking', readonly=1)
    name = fields.Char(related='batch_id.name', readonly=1)
    partner_id = fields.Many2one(related='batch_id.partner_id', readonly=1)
    date = fields.Date(related='batch_id.date', readonly=1, string="Fecha")
    excess = fields.Boolean(related='batch_id.excess', readonly=1, string="Franquicia actual")
    new_excess = fields.Boolean('Franquicia a aplicar')

class BatchExcessWzd(models.TransientModel):

    _name = 'batch.excess.wzd'

    date = fields.Datetime('Cierre de agencia', readonly=1)
    excess_ids = fields.Many2many('batch.excess.line', string="CON franquicia", domain=[('new_excess', '=', True)])
    lines = fields.Many2many('batch.excess.line', string="CON franquicia")
    not_excess_ids = fields.Many2many('batch.excess.line', string="SIN franquicia", domain=[('new_excess', '=', False)])
    picking_type_id = fields.Many2one('stock.picking.type')
    new_date = fields.Datetime('Nueva hora de cálculo')
    hide_no_excess = fields.Boolean("Mostrar/coultar sin franquicia", default=True)

    def get_line_values(self, id, excess=False):
        batch = self.env['stock.batch.picking'].browse(id)
        vals = {'batch_id': batch.id,
                'name': batch.name,
                'partner_id': batch.partner_id.id,
                'date': batch.date_done or batch.date,
                'excess': batch.excess,
                'new_excess': excess}
        return vals

    @api.model
    def default_get(self, fields):
        return super().default_get(fields)


    @api.multi
    def action_apply_changes(self):

        lines = self.excess_ids + self.not_excess_ids
        batch_ids = self.env['stock.batch.picking']

        for line in lines.filtered(lambda x: x.excess != x.new_excess):
            batch_ids += line.batch_id
            line.batch_id.excess = line.new_excess

        if batch_ids:
            partner_ids = batch_ids.mapped('partner_id')
            batch_ids = lines.mapped('batch_id').filtered(lambda x: x.partner_id in partner_ids).ids
            ctx = self._context.copy()
            ctx.update(from_time=self.date)
            domain = self.with_context(ctx).picking_type_id.get_excess_domain()
            return self.picking_type_id.return_action_show_batch_picking(domain=domain)



    @api.multi
    def action_apply_new_date(self):
        ctx = self._context.copy()
        ctx.update(from_time=self.new_date)
        return self.with_context(ctx).picking_type_id.open_excess_wzd()





