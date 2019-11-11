# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class StockMove(models.Model):
    _inherit = 'stock.move'

    ic_sale_line_id = fields.Many2one('sale.order.line', 'Sale Line')

    def _assign_picking_post_process(self, new=False):
        super(StockMove, self)._assign_picking_post_process(new=new)
        if self.ic_sale_line_id:
            self.picking_id.sudo().write({'ic_sale_ids': [(4, self.sudo().ic_sale_line_id.order_id.id)]})

    @api.model
    def _prepare_merge_moves_distinct_fields(self):
        distinct_fields = super(StockMove, self)._prepare_merge_moves_distinct_fields()
        distinct_fields.append('ic_sale_line_id')
        return distinct_fields

    @api.model
    def _prepare_merge_move_sort_method(self, move):
        move.ensure_one()
        keys_sorted = super(StockMove, self)._prepare_merge_move_sort_method(move)
        keys_sorted.append(move.ic_sale_line_id.id)
        return keys_sorted

    def _action_done(self):
        result = super(StockMove, self)._action_done()
        for line in result.mapped('ic_sale_line_id').sudo():
            line.qty_delivered = line._get_delivered_qty()
        return result

    @api.multi
    def write(self, vals):
        res = super(StockMove, self).write(vals)
        if 'product_uom_qty' in vals:
            for move in self:
                if move.state == 'done':
                    sale_order_lines = self.filtered(
                        lambda move: move.ic_sale_line_id and move.product_id.expense_policy in [False, 'no']).mapped(
                        'ic_sale_line_id')
                    for line in sale_order_lines.sudo():
                        line.qty_delivered = line._get_delivered_qty()
        return res

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    auto_purchase_order_id = fields.Many2one(related='sale_id.auto_purchase_order_id', string="")
    ic_pick_id = fields.Char(string="IC pick", compute="compute_ic_pick_id",
                             help="Albarán de salida correspondiente")
    ic_sale_ids = fields.Many2many('sale.order', string='IC venta')

    @api.multi
    def compute_ic_pick_id(self):
        for pick in self.filtered(lambda x: x.ic_sale_ids):
            ic_sale_ids = pick.sudo().ic_sale_ids
            if ic_sale_ids.mapped('picking_ids'):
                pick.ic_pick_id = "{} > {}".format(pick.name, (x.name for x in ic_sale_ids.mapped('picking_ids')))

    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if self._context.get('auto_purchase_order_id', False):
            args += [('sale_id.auto_purchase_order_id', '!=', False)]
        elif not self._context.get('auto_purchase_order_id', True):
            args += [('sale_id.auto_purchase_order_id', '=', False)]
        return super().search(args, offset=offset, limit=limit, order=order, count=count)

    @api.multi
    def action_done(self):
        #print ("Entro action done de {}".format(self.name))
        #import ipdb; ipdb.set_trace()

        res = super().action_done()
        ctx = self._context.copy()
        for pick in self:
            if pick.intercompany_picking_id:
                dest_pick_ids = pick.move_lines.filtered(lambda x: x.state == 'done').mapped('move_dest_ids').mapped('picking_id')
                ic_user = pick.company_id.intercompany_user_id.id
                ic_company = pick.company_id.id

                ctx.update(force_company=ic_company)
                for move_line in dest_pick_ids.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty
                dest_pick_ids.with_context(ctx).sudo(ic_user).action_done()

        return res



