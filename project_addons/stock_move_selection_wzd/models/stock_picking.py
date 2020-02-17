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

    group_code = fields.Many2one(related='picking_type_id.group_code')
    sga_integrated = fields.Boolean('Sga', help='Marcar si tiene un tipo de integración con el sga')
    sga_state = fields.Selection(SGA_STATES, default='no_integrated', string="SGA Estado", copy=False)
    batch_delivery_id = fields.Many2one(related='batch_picking_id.batch_delivery_id', store=True, string='Orden de carga')
    excess = fields.Boolean(string='Franquicia')
    count_move_lines = fields.Integer('Nº líneas', compute="_get_nlines")
    delivery_route_group_id = fields.Many2one('delivery.route.path.group', 'Grupo de entrega', store=False)
    to_batch = fields.Many2one('stock.batch.picking', store=False)

    @api.multi
    @api.depends('state', 'is_locked')
    def _compute_show_validate(self):
        picking_with_batch = self.move_line_ids.filtered(lambda x: x.batch_picking_id).mapped('picking_id')
        for picking in picking_with_batch:
            picking.show_validate = False
        super(StockPicking, self - picking_with_batch)._compute_show_validate()

    @api.multi
    def _get_nlines(self):
        for pick in self:
            pick.count_move_lines = len(pick.move_lines)

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


    def get_batch_domain(self):
        domain = super().get_batch_domain()
        delivery_id = self.move_line_ids.mapped('batch_delivery_id')
        if delivery_id:
            domain += [('batch_delivery_id', '=', delivery_id.id)]
        return domain

    def add_picking_to_expedition(self):
        picking_ids = self.filtered(lambda x: x.to_batch != False)
        picking_ids.write({'batch_picking_id': picking_ids[0].to_batch})

    @api.multi
    def _assign_picking_batch(self):
        if any(x.batch_picking_id for x in self):
            raise ValidationError (_('Hay albaranes que ya tienen un batch asignado: {}'.format(self.filtered(lambda x: x.batch_picking_id).mapped('name'))))
        batch_ids = self.env['stock.batch.picking']
        for picking in self:
            batch_domain = picking.get_batch_domain()
            batch_id = self.env['stock.batch.picking'].search(batch_domain)
            if not batch_id:
                batch_id = picking.create_batch_picking()
            picking.batch_picking_id = batch_id
            batch_ids |= batch_id
        return batch_ids

    def get_values_for_new_batch(self):
        return {'batch_delivery_id': self.batch_delivery_id,
                     'shipping_type': self.shipping_type,
                     'delivery_route_path_id': self.delivery_route_path_id.id,
                     'payment_term_id': self.payment_term_id.id,
                     'picking_type_id': self.picking_type_id.id,
                     'partner_id': self.partner_id.id,
                     }

    def create_batch_picking(self):
        batch_vals= self.get_values_for_new_batch()
        return self.env['stock.batch.picking'].create(batch_vals)

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
        if not self._context.get('from_sga', False) and any(x.batch_picking_id for x in self):
            raise ValidationError (_("No puedes validar un albarán asignado a un batch"))


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
        self.write({'batch_picking_id': False})


    @api.multi
    def transfer_package(self, package_id, location_dest_id, auto=False, unpack=False):

        picking_id = self.env['stock.picking']
        quant_ids = self.env['stock.quant'].search([('package_id', '=', package_id)])
        if not quant_ids:
            return False
        location_id = quant_ids[0].location_id.id

        if not (picking_id and picking_id.location_id == location_id):
            domain = [('default_location_src_id', '=', location_id),
                      ('default_location_dest_id', '=', location_dest_id), ]
            picking_type_id = self.env['stock.picking.type'].search(domain, limit=1)
            if not picking_type_id:
                domain =[('code', '=', 'internal')]
                picking_type_id = self.env['stock.picking.type'].search(domain, limit=1)
            vals = {'picking_type_id': picking_type_id.id,
                    'location_id': location_id,
                    'location_dest_id': location_dest_id,
                    }
            picking_id = self.create(vals)
        sml = self.env['stock.move.line']
        for quant in quant_ids:
            sml_vals = {'product_id': quant.product_id.id,
                        'location_id': quant.location_id.id,
                        'location_dest_id': location_dest_id,
                        'qty_done': quant.quantity,
                        'package_id': package_id,
                        'result_package_id': unpack and False or package_id,
                        'picking_id': picking_id.id,
                        'product_uom_id': quant.product_uom_id.id
                        }
            if unpack:
                sml_vals['result_package_id'] = False
            sml.create(sml_vals)
        if auto:
            picking_id.do_transfer()
        return picking_id

    @api.multi
    def action_add_to_batch_delivery(self):
        if any(x.state in ('done', 'cancel') for x in self):
            raise ValidationError (_('Estado incorrecto para los pedidos: {}'.format([x.name for x in self.filtered(lambda x: x.state in ('cancel', 'done'))])))
        if len(self) == 1:
            if self.batch_delivery_id:
                self.move_lines.filtered(lambda x: x.state != 'done').write({'batch_delivery_id': False})
                self.batch_delivery_id = False
                return

        action = self.env.ref('stock_move_selection_wzd.batch_delivery_wzd_act_window').read()[0]
        return action



    @api.multi
    def action_add_to_batch_picking(self):

        if self._context.get('default_batch_picking_id', False) and len(self) == 1:
            self.write({'batch_picking_id': self._context['default_batch_picking_id']})
            return

        if any(x.state in ('done', 'cancel') for x in self):
            raise ValidationError (_('Estado incorrecto para los pedidos: {}'.format([x.name for x in self.filtered(lambda x: x.state in ('cancel', 'done'))])))
        to_add = self.filtered(lambda x: not x.batch_picking_id)
        to_remove = self.filtered(lambda x: x.batch_picking_id)

        if to_add and to_remove:
            raise ValidationError (_('Selección inconsiste. Hay movimientos con y sin batch'))
        if to_remove:
            to_remove.write({'batch_picking_id': False})
        elif to_add:
            ctx = self._context.copy()
            if 'active_domain' in ctx.keys():
                ctx.pop('active_domain')
            obj = self.env['stock.batch.picking.wzd']
            wzd_id = obj.create_from('stock.picking', to_add.ids)
            action = wzd_id.get_formview_action()
            action['target'] = 'new'
            return action