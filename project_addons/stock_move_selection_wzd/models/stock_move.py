# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .stock_picking_type import PICKING_TYPE_GROUP
from .stock_picking_type import SGA_STATES

class ProcurementRule(models.Model):
    _inherit = 'procurement.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_id, name, origin, values, group_id):
        vals = super()._get_stock_move_values(product_id=product_id,
                                              product_qty=product_qty,
                                              product_uom=product_uom,
                                              location_id=location_id,
                                              name=name,
                                              origin=origin,
                                              values=values,
                                              group_id=group_id)

        if values.get('sale_line_id', False):
            sol = self.env['sale.order.line'].browse(values['sale_line_id'])
            vals.update({'campaign_id': sol.campaign_id and sol.campaign_id.id,
                         'carrier_id': sol.order_id.carrier_id and sol.order_id.carrier_id.id,
                         'sga_integrated': self.picking_type_id.sga_integrated,
                         'sga_state': 'NE' if self.picking_type_id.sga_integrated else 'NI'})

        return vals



class StockMove(models.Model):
    _inherit = 'stock.move'


    ##NEcesito traer estos campos de stock_move_line
    package_id = fields.Many2one('stock.quant.package', 'Source Package', ondelete='restrict')
    lot_id = fields.Many2one('stock.production.lot', 'Lot')
    result_package_id = fields.Many2one(
        'stock.quant.package', 'Destination Package',
        ondelete='restrict', required=False,
        help="If set, the operations are packed into this package")
    dunmy_picking_id = fields.Many2one('stock.picking', 'Transfer Reference', store=False)

    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_state = fields.Selection(SGA_STATES, default='NI', string="SGA Estado")


    def get_new_location_vals(self, location_field, location):
        vals = super().get_new_location_vals(location_field, location)

        if location.picking_type_id and vals:
            vals.update(sga_integrated = location.picking_type_id.sga_integrated,
                        sga_state='NE' if location.picking_type_id.sga_integrated else 'NI')
        return vals

    def get_new_vals(self):
        vals = super().get_new_vals()
        vals.update(sga_integrated=self.picking_type_id and self.picking_type_id.sga_integrated,
                    sga_state='NE' if self.picking_type_id.sga_integrated else 'NI')
        print (vals)
        return vals


    def get_moves_selection_domain(self, group_code=''):
        wh_ids = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)])
        lot_stock = wh_ids.mapped('lot_stock_id')
        domain = []
        if group_code:
            domain += [('picking_type_id.group_code', '=', group_code)]
        domain += [('state', 'not in', ['draft', 'cancel', 'done'])]
        print(domain)
        return domain

    @api.multi
    def _return_action_show_moves(self, group_code=''):
        tree = self.env.ref('stock_move_selection_wzd.view_move_line_tree_sel', False)
        kanban = self.env.ref('stock_move_selection_wzd.view_move_sel_kanban', False)
        action = self.env.ref(
            'stock_move_selection_wzd.stock_move_sel_action2').read()[0]
        action['domain'] = self.get_moves_selection_domain(group_code)
        action['views'] = [(tree and tree.id or False, 'tree'),
                           (kanban and kanban.id or False, 'kanban')]

        action['context'] = {group_code if group_code else 'all': True,
                             'show_partner': group_code in ['internal', 'location', 'reposition'],
                             'show_date': group_code in ['incoming', 'outgoing'],
                             'search_default_todo': 1,
                             'search_default_without_pick': 1}

        name_str = [x[1] for x in PICKING_TYPE_GROUP if x[0] == group_code]
        if name_str:
            action['display_name'] = "---------> {} Moves".format(name_str[0])
        return action

    def get_domain_moves_to_asign(self):
        return self.filtered(lambda x: not x.picking_id and x.state not in ('done', 'cancel', 'draft'))


    @api.multi
    def move_sel_assign_picking(self):
        for move in self.get_domain_moves_to_asign():
            move.action_force_assign_picking()

    def get_domain_moves_to_deasign(self):
        return self.filtered(lambda x: x.picking_id and x.state not in ('done', 'cancel', 'draft'))

    @api.multi
    def move_de_sel_assign_picking(self):
        self.picking_id = False
        self.move_line_ids.write({'picking_id':False})


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_state = fields.Selection(SGA_STATES, default='NI', string="SGA Estado")

    @api.multi
    def write(self, vals):

        move_vals = {}

        for f in ['package_id', 'result_package_id']:
            if f in vals:
                move_vals.update({f: vals[f]})

        if move_vals:
            for line in self:
                line.move_id.write(move_vals)

        return super().write(vals)
