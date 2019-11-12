# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT


from .stock_picking_type import SGA_STATES
from odoo.osv import expression

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def get_draft_batch_picking_id(self):

        for pick in self:
            draft_batch_picking_id = pick.move_lines.mapped('draft_batch_picking_id')
            if len(draft_batch_picking_id) == 1:
                pick.draft_batch_picking_id = draft_batch_picking_id
            else:
                pick.draft_batch_picking_id = False


    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado", copy=False)
    #state = fields.Selection(selection_add=[('packaging', 'Empaquetado')])
    batch_delivery_id = fields.Many2one('stock.batch.delivery', string='Orden de carga', copy=False, store=False, compute="get_batch_delivery_id")
    draft_batch_picking_id = fields.Many2one('stock.batch.picking', 'Batch', compute="get_draft_batch_picking_id")

    excess = fields.Boolean(string='Franquicia')
    count_move_lines = fields.Integer('Nº líneas', compute="_get_nlines")
    dunmy_route_group_id = fields.Many2one('delivery.route.path.group', 'Grupo de entrega', store=False)

    @api.multi
    def _get_nlines(self):
        for pick in self:
            pick.count_move_lines = len(pick.move_lines)

    @api.multi
    def get_batch_delivery_id(self):

        for pick in self:
            batch_delivery_id = pick.move_lines.mapped('batch_delivery_id')
            if len(batch_delivery_id) == 1:
                pick.batch_delivery_id = batch_delivery_id
            else:
                pick.batch_delivery_id = False

    def create_second_pick(self, second_moves=[]):
        """ Copy of create backorder
        """
        second_pick = self.env['stock.picking']
        if second_moves:
            second_pick = self.copy({
                    'name': '/',
                    'move_lines': [],
                    'move_line_ids': [],
                    'second_id': self.id
                })
            self.message_post(
                _('The backorder <a href=# data-oe-model=stock.picking data-oe-id=%d>%s</a> has been created.') % (
                    second_pick.id, second_pick.name))
            second_moves.write({'picking_id': second_pick.id})
            second_moves.mapped('move_line_ids').write({'picking_id': second_pick.id})
            second_pick.action_assign()
        return second_pick

    @api.model
    def create(self, vals):

        if len(vals) == 1 and vals.get('name', False):
            domain = [('name', '=', vals.get('name', False))]
            picking_type_id = self.env['stock.picking.type'].search(domain)
            if not picking_type_id:
                raise ValidationError (_("Not pick for '%s'") % vals.get('name', False))
            if len(picking_type_id)>1:
                raise ValidationError (_("More than 1 pick for '%s'") % vals.get('name', False))
            vals.update(picking_type_id=picking_type_id.id,
                        sga_integrated=picking_type_id.get_sga_integrated(),
                        sga_state = 'no_send' if picking_type_id.get_sga_integrated() else 'no_integrated',
                        location_id=picking_type_id.default_location_src_id.id,
                        location_dest_id=picking_type_id.default_location_dest_id.id)
            vals.pop('name')
        return super().create(vals)


    def action_send_to_sga(self):
        return self.send_to_sga()

    @api.multi
    def send_to_sga(self):
        ##PARA HEREDAR EN ULMA Y ADAIA
        return True

    @api.multi
    def button_validate(self):
        if not self._context.get('from_sga', False) and any(x.batch_picking_id or x.draft_batch_picking_id for x in self):
            raise ValidationError (_("No puedes validar un albarán asigado a un batch"))
        return super().button_validate()

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):

        if self._context.get('para_hoy', False):
            today = fields.Date.today()
            hoy = ('date_expected', '>=', today)
            ayer = ('date_expected', '<', today)
            d_1 = expression.AND([[hoy], ['&', ('picking_id', '!=', False), ('state', 'not in', ('draft', 'cancel'))]])
            d_2 = ['&', ayer, ('state', 'in', ('assigned', 'confirmed', 'partially_available'))]
            domain = expression.OR([d_1,d_2])
            moves = self.env['stock.move'].read_group(domain, ['picking_id'], ['picking_id'])
            picking_ids = [x['picking_id'][0] for x in moves if x['picking_id']]
            args_para_hoy = [('id', 'in', picking_ids)]
            args = expression.normalize_domain(args)
            args = expression.AND([args_para_hoy, args])
        return super().search(args, offset=offset, limit=limit, order=order, count=count)

    @api.multi
    def _add_delivery_cost_to_so(self):
        return True


    @api.multi
    def button_unlink_from_batch(self):
        draft_batch_picking_id = self._context.get('draft_batch_picking_id', False)
        if draft_batch_picking_id:
            moves = self.mapped('move_lines').filtered(lambda x: x.draft_batch_picking_id==draft_batch_picking_id)
            moves.button_unlink_from_batch()
