# -*- coding: utf-8 -*-
# Copyright 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.exceptions import UserError,ValidationError
from odoo.addons.shipping_type.models.info_route_mixin import SHIPPING_TYPE_SEL, DEFAULT_SHIPPING_TYPE, STRING_SHIPPING_TYPE, HELP_SHIPPING_TYPE


class DeliveryPartnerOrder(models.Model):

    _name = 'delivery.partner.order'
    _order = 'delivery_id, sequence asc'

    delivery_id = fields.Many2one('stock.batch.delivery', 'Orden de carga')
    partner_id = fields.Many2one('res.partner')
    sequence = fields.Integer(string="Sequence", default=10)
    city = fields.Char(related='partner_id.city')
    zip = fields.Char(related='partner_id.zip')

class StockBatchDelivery(models.Model):
    """ This object allow to manage multiple stock.batch.delivery
    """

    _inherit = ['info.route.mixin', 'mail.thread', 'mail.activity.mixin']
    _name = 'stock.batch.delivery'



    @api.multi
    def _get_dates(self):
        for batch in self:
            if batch.move_lines:
                batch.date_expected = min((move.date_expected or move.date) for move in batch.move_lines)

    @api.onchange('date_expected')
    def _set_dates(self):
        for batch in self:
            batch.move_lines.write({'date_expected': batch.date_expected})

    @api.model
    def get_batch_domain(self):
        bp = self and self[0]
        if bp:
            domain = [('state', 'in', ('assigned', 'done')), ('picking_type_id', '=', bp.picking_type_id.id)]

        else:
            domain=[('state', 'in', ('assigned', 'done'))]
        return domain

    name = fields.Char(
        'Name',
        required=True, index=True,
        copy=False, unique=True,
        states={'draft': [('readonly', False)]},
        default=lambda self: self.env['ir.sequence'].next_by_code(
            'stock.batch.delivery'
        ),
    )
    state = fields.Selection([
        ('draft', 'Borrador'),
        ('ready', 'Preparada'),
        ('done', 'Realizada'),
        ('cancel', 'Cancelada')],
        string='State',
        readonly=True, index=True, copy=False,
        default='draft',
        help='the state of the batch packages. '
        'Workflow is draft -> assigned -> done or cancel'
    )
    picking_type_id = fields.Many2one('stock.picking.type', 'Tipo de operación')
    date_expected = fields.Date(
        'Fecha prevista',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'ready': [('readonly', False)]
        },
        compute=_get_dates,
        inverse=_set_dates,
        help='date on which the batch picking is to be processed'
    )
    date_done = fields.Date(  'Date',
        required=True, readonly=True,
        default=fields.Date.context_today,
        help='date on which the batch picking is processed'
    )
    picker_id = fields.Many2one(
        'res.users', 'Operario',
        readonly=True, index=True,
        states={
            'ready': [('readonly', False)]
        },
        help='the user who prepare this batch'
    )
    batch_ids = fields.One2many('stock.batch.picking', 'batch_delivery_id', string='Grupo')
    picking_ids = fields.One2many('stock.picking', 'batch_delivery_id', string='Albaranes', help='List of picking related to this batch.')

    count_batch_ids = fields.Integer('Nº albaranes', compute='_get_picking_ids')
    count_picking_ids = fields.Integer('Nº pedidos', compute='_get_picking_ids')

    move_lines = fields.One2many(
        'stock.move', 'batch_delivery_id',
        string='Movimientos',
        help='List of picking related to this batch.'
    )
    count_move_lines = fields.Integer('Nº líneas', compute='_get_picking_ids')
    move_line_ids = fields.One2many(
        'stock.move.line', 'batch_delivery_id',
        string='Operaciones',
        help='List of picking related to this batch.'

    )
    partner_picking_ids = fields.One2many('res.partner', compute='_get_picking_ids', string="Empresa")
    count_partner_ids = fields.Integer('Nº clientes', compute='_get_picking_ids')
    package_ids = fields.One2many(
        'stock.quant.package', 'batch_delivery_id',
        string='Paquetes',
        help='Those are the entire packages of a picking shown in the view of '
             'operations',
    )
    count_package_ids = fields.Integer('Nº paquetes', compute='_get_picking_ids')
    notes = fields.Text('Notas', help='free form remarks')

    driver_id = fields.Many2one('res.partner', string='Conductor',
                                      help='Carrier driver for this batch picking.',
                                      domain="[('route_driver', '=', True)]")
    plate_id = fields.Many2one('delivery.plate', string='Matrícula', help='Plate for this batch picking.')

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get(),
        index=True, required=True)
    carrier_id = fields.Many2one("delivery.carrier", string="Carrier")
    shipping_type = fields.Selection(selection=SHIPPING_TYPE_SEL, string="Envío")
    #delivery_route_path_id = fields.Many2one('delivery.route.path', string="Ruta")
    # payment_term_id = fields.Many2one('account.payment.term', string='Plazos de pago', compute='compute_route_fields',
    #                                   inverse='set_route_fields', store=True)
    weight = fields.Float(
        'Peso', digits=2,
        help="The weight of the contents in Kg, not including any packaging, etc.")
    partner_order_ids = fields.One2many('delivery.partner.order', 'delivery_id', string="Partner order")
    delivery_route_path_ids = fields.Many2many('delivery.route.path', string="Rutas de transporte")
    partner_ids = fields.Many2many('res.partner', string ="Clientes", help = "Campo para filtrar por clientes")
    payment_term_ids = fields.Many2many('account.payment.term', string='Plazos de pago')

    #
    # @api.multi
    # @api.depends('move_lines.shipping_type', 'move_lines.delivery_route_path_id', 'move_lines.carrier_id')
    # def compute_route_fields(self):
    #     for pick in self:
    #         moves = pick.move_lines
    #         # if any(move.state == 'done' for move in moves):
    #         #    raise ValidationError (_('No puedes cambiar en movimientos ya realizados'))
    #         if moves:
    #             shipping_type_ids = []
    #             for move in moves:
    #                 if move.shipping_type in shipping_type_ids:
    #                     continue
    #                 shipping_type_ids.append(move.shipping_type)
    #             if shipping_type_ids[0] and len(shipping_type_ids) == 1:
    #                 pick.shipping_type = shipping_type_ids[0]
    #             delivery_route_path_ids = moves.mapped('delivery_route_path_id')
    #             if len(delivery_route_path_ids) == 1:
    #                 pick.delivery_route_path_id = delivery_route_path_ids[0]
    #             carrier_ids = moves.mapped('carrier_id')
    #             if len(carrier_ids) == 1:
    #                 pick.carrier_id = carrier_ids[0]
    #             payment_term_ids = moves.mapped('payment_term_id')
    #             if len(payment_term_ids) == 1:
    #                 pick.payment_term_id = payment_term_ids[0]
    #
    # def check_allow_change_route_fields(self):
    #     return True
    #     if any(move.state == 'done' for move in self.move_lines):
    #         raise ValidationError(_('No puedes cambiar en movimientos ya realizados'))
    #     return True
    #
    # @api.multi
    # def set_route_fields(self):
    #     for pack in self:
    #         pack.check_allow_change_route_fields()
    #         moves = pack.move_line_ids.mapped('move_id')
    #
    #         vals = {}
    #         if pack.shipping_type:
    #             vals.update({'shipping_type': pack.shipping_type})
    #         if pack.delivery_route_path_id:
    #             vals.update({'delivery_route_path_id': pack.delivery_route_path_id.id})
    #         if pack.carrier_id:
    #             vals.update({'carrier_id': pack.carrier_id.id})
    #         if pack.payment_term_id:
    #             vals.update({'payment_term_id': pack.payment_term_id.id})
    #         moves.write(vals)

    @api.multi
    def update_partner_order(self):
        rpo = self.env['route.partner.order']
        dpo = self.env['delivery.partner.order']

        route_id = fields.Many2one('delivery.route.path')
        sequence = fields.Integer('Orden en ruta', default=10)
        partner_id = fields.Many2one('res.partner', 'Cliente', domain=[('customer', '=', True)])

        for delivery in self:
            delivery.partner_order_ids.unlink()
            route_ids = delivery.delivery_route_path_ids
            #partner_picking_ids = delivery.partner_picking_ids
            #if not partner_picking_ids:
            partner_picking_ids = delivery.picking_ids.partner_id
            route_partner = []
            if route_ids:
                if len(route_ids) == 1:
                    w1 = 'route_id = {}'.format(route_ids.id)
                else:
                    w1 = 'route_id in {}'.format(tuple(route_ids.ids))

                if len(partner_picking_ids) == 1:
                    w2 = 'partner_id = {}'.format(partner_picking_ids.id)
                else:
                    w2 = 'partner_id in {}'.format(tuple(partner_picking_ids.ids))

                if route_ids and partner_picking_ids:
                    sql = "select min(sequence), partner_id from route_partner_order where {} and {} group by partner_id".format(w1, w2)
                    self._cr.execute(sql)
                    res = self._cr.fetchall()
                    print (sql)
                    print(res)

                    for val in res:
                        values = {'delivery_id': delivery.id,
                                  'partner_id': val[1],
                                  'sequence': val[0]}
                        route_partner.append(val[1])
                        dpo.create(values)


            for p_id in partner_picking_ids.filtered(lambda x: x.id not in route_partner):
                values = {'delivery_id': delivery.id,
                          'partner_id': p_id.id,
                          'sequence': 10}
                dpo.create(values)




    def get_delivery_info(self, partner_id=False):

        move_lines = self.move_lines
        if partner_id:
            move_lines = move_lines.filtered(lambda x:x.partner_id == partner_id)
        picking_ids = move_lines.mapped('picking_id')
        move_line_ids = move_lines.mapped('move_line_ids')
        package_ids = move_line_ids.mapped('result_package_id')
        package_packaging_ids = package_ids.mapped('packaging_line_ids')
        sbp_ids = move_lines.mapped('batch_picking_id')
        vals ={
            'picking_ids': picking_ids,
            'batch_ids': sbp_ids,
            'move_line_ids': move_line_ids,
            'partner_ids': move_lines.mapped('partner_id'),
            'package_ids': package_ids,
            'count_picking_ids': len(sbp_ids),
            'count_move_lines': len(move_lines),
            'count_package_ids': len(package_ids),
            'count_package_packaging_ids': sum(x.qty for x in package_packaging_ids)
        }
        return vals

    @api.multi
    def unlink(self):
        if any(x.state == 'done' for x in self):
            raise ValidationError(_('No puedes boorar una orden de carga ya realizada'))
        super().unlink()

    @api.multi
    def _get_picking_ids(self):
        for delivery_id in self:
            delivery_id.count_package_ids = len(delivery_id.package_ids)
            delivery_id.count_batch_ids = len(delivery_id.batch_ids)
            delivery_id.count_picking_ids = len(delivery_id.picking_ids)
            delivery_id.count_move_lines = len(delivery_id.move_lines)
            delivery_id.partner_picking_ids = delivery_id.picking_ids.mapped('partner_id')
            delivery_id.count_partner_ids = len(delivery_id.partner_picking_ids)


    @api.multi
    def action_transfer(self):
        for batch in self.filtered(lambda x:x.state=='ready'):
            batch.batch_ids.action_transfer()
            batch.state = 'done'

    @api.multi
    def action_draft(self):
        self.ensure_one()
        self.write({'state': 'draft'})

        batch_ids = self.batch_ids
        if any(x.state == 'done' for x in batch_ids):
            raise ValidationError (_('No cancelar una orden de entrega si un albarán está marcado como realizado'))
        batch_ids.write({'batch_delivery_id': False})
        batch_ids.unlink()
        self.partner_order_ids.unlink()

    @api.multi
    def action_confirm(self):
        self.write({'state': 'ready'})

    @api.multi
    def action_view_delivery_partner_orders(self):

        self.ensure_one()
        action = self.env.ref('stock_move_selection_wzd.action_show_delivery_partner_orders').read([])[0]
        action['domain'] = [('id', 'in', self.partner_order_ids.ids)]
        action['context'] = {'default_delivery_id': self.id}
        return action

    @api.multi
    def action_view_stock_package(self):
        """This function returns an action that display existing packages of
        given batch picking.
        """
        self.ensure_one()


        action = self.env.ref('stock.action_package_view').read([])[0]
        action['domain'] = [('id', 'in', self.package_ids.ids)]
        return action

    @api.multi
    def action_view_stock_batch_picking(self):


        self.ensure_one()
        action = self.env.ref('stock_batch_picking.action_stock_batch_picking_tree').read([])[0]
        action['domain'] = [('id', 'in', self.batch_ids.ids)]
        return action

    @api.multi
    def action_view_stock_move(self):
        self.ensure_one()
        action = self.env.ref('stock_move_selection_wzd.stock_move_sel_action2').read([])[0]
        action['domain'] = [('id', 'in', self.move_lines.ids)]
        action['context'] = self.move_lines and self.move_lines[0].picking_type_id.update_context() or {}
        return action


    @api.multi
    def print_rda_delivery(self):
        raise UserError(_('No implementado.'))
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        else:
            active_ids = []
            for batch in self:
                active_ids.append(batch.id)
            return self.env.ref('adr_product.delivery_batch_adr_report').with_context(active_ids=active_ids,
                                                                                      active_model='stock.batch.picking',
                                                                                      pickings=pickings).report_action([])
    @api.multi
    def get_info_route_batch_delivery(self):
        for obj in self:
            if obj.shipping_type or obj.delivery_route_path_id:
                if 'carrier_id' in obj.fields_get_keys():
                    carrier_id = obj.carrier_id and obj.carrier_id.name or ''
                else:
                    carrier_id = ''

                name2 = '{} {}'.format(obj.delivery_route_path_id.name or 'Sin ruta', carrier_id)
                shipping_type = obj._fields['shipping_type'].convert_to_export(obj.shipping_type,
                                                                               obj) if obj.shipping_type else 'Sin envío'
                obj.info_route_str = '{}: {}'.format(shipping_type, name2)
            else:
                obj.info_route_str = False


    @api.multi
    def action_show_filter_wzd(self):

        self.ensure_one()
        val = {'delivery_id': self.id,
               'type': 'package',
               'shipping_type_ids': self.shipping_type,
               'delivery_route_path_ids': [(6,0,self.delivery_route_path_id.ids)],
               'partner_ids': [(6,0, self.partner_ids.ids)],
               'package_ids': [(6,0, self.package_ids.ids)],
               'move_ids': [(6,0,self.move_ids.ids)],
               'move_line_ids': [(6, 0, self.move_line_ids.ids)],
               'picking_ids': [(6, 0, self.picking_ids.ids)]}


        new_wzd = self.env[('stock.batch.delivery.filter.wzd')].create(val)

        self.ensure_one()
        action = self.env.ref('stock_move_selection_wzd.action_batch_delivery_filter').read([])[0]
        action['res_id'] = new_wzd.id
        return action
