# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from pprint import pprint


class StockDeliveryBatch(models.Model):
    _name = "stock.delivery.batch"
    _inherit = ['mail.thread']
    _description = "Delivery Batch"
    _order = "name desc"

    name = fields.Char(
        string='Delivery Batch Name', default='New',
        copy=False, required=True,
        help='Name of the delivery batch picking')
    user_id = fields.Many2one(
        'res.users', string='Responsible', track_visibility='onchange',
        help='Person responsible for this batch picking')
    carrier_id = fields.Many2one(
        'delivery.carrier', string='Delivery carrier', track_visibility='onchange',
        help='Delivery carrier for this batch picking.')
    picking_ids = fields.One2many(
        'stock.picking', 'delivery_batch_id', string='Pickings',
        help='List of picking associated to this batch')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'Running'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], default='draft',
        copy=False, track_visibility='onchange', required=True)
    delivery_data = fields.Char(string="Vehicle plates")
    delivery_date = fields.Date(string='Delivery date')

    @api.model
    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].next_by_code('delivery.batch') or '/'
        return super(StockDeliveryBatch, self).create(vals)

    @api.multi
    def confirm_picking(self):
        pickings_todo = self.mapped('picking_ids')
        self.write({'state': 'in_progress'})
        return pickings_todo.action_assign()

    @api.multi
    def cancel_picking(self):
        self.mapped('picking_ids').action_cancel()
        return self.write({'state': 'cancel'})

    @api.multi
    def print_picking(self):
        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))
        return self.env.ref('stock.action_report_picking').with_context(active_ids=pickings.ids, active_model='stock.picking').report_action([])
    
    @api.multi
    def print_rda_delivery(self):
        adr_picks = []
        partners_data = []
        partners_index = []
        partner_pickings = []
        exe11363_total_weight = 0.0
        exe11364_total_weight = 0.0
        exe22315_total_weight = 0.0
        category_max_weight = 0
        regular_total_weight = 0
        lq_total_weight = 0.0
        counter_22315 = 0
        counter_lq = 0
        exention_type = None

        categories_ids = []
        docs = []

        pickings = self.mapped('picking_ids')
        if not pickings:
            raise UserError(_('Nothing to print.'))

        for pick in pickings:
            if pick.adr:
                adr_picks.append(pick)
                for line in pick.move_lines:

                    if line.product_tmpl_id.adr_idnumonu:
                        ## Metemos el id en partners para tener un listado de los destinatarios. 
                        if not line.partner_id.id in partners_index:
                            partners_index.append(line.partner_id.id)
                            partners_data.append({
                                'id': line.partner_id.id,
                                'name': line.partner_id.name
                            })
                        
                        partner_pickings.append({
                            'partner_id': line.partner_id.id,
                            'line_id': line.id,
                            'origin': line.origin,
                            'name': line.product_tmpl_id.name,
                            'default_code': line.product_tmpl_id.default_code,
                            'adr_denomtecnica': line.product_tmpl_id.adr_idnumonu.denomtecnica,
                            'adr_qty_limit': line.product_tmpl_id.adr_idnumonu.qty_limit,
                            'product_qty': line.product_qty,
                            'adr_bultodesc': line.product_tmpl_id.adr_idnumonu.bultodesc,
                            'packing_group': line.product_tmpl_id.adr_idnumonu.packing_group,
                            'official_name': line.product_tmpl_id.adr_idnumonu.official_name,
                            'ranking_id': line.product_tmpl_id.adr_idnumonu.ranking_id,
                            't_code': line.product_tmpl_id.adr_idnumonu.t_code,
                            'adr_exe22315': line.product_tmpl_id.adr_idnumonu.exe22315,
                            'adr_peligroma': line.product_tmpl_id.adr_idnumonu.peligroma,
                            'adr_weight_x_kgrs_11363': line.product_tmpl_id.adr_weight_x_kgrs_11363*line.product_qty,
                            'adr_weight_x_kgrs_11364': line.product_tmpl_id.adr_weight_x_kgrs_11364*line.product_qty,
                            'adr_acc_signals': line.product_tmpl_id.adr_idnumonu.acc_signals,
                            'adr_idnumonu': line.product_tmpl_id.adr_idnumonu.numero_onu,
                            'adr_regular_weight': line.product_tmpl_id.weight*line.product_qty
                            #'weight': line.product_tmpl_id.weight,
                            #'x_kgrs_11363': line.product_tmpl_id.adr_idnumonu.adr_category_id.x_kgrs_11363,
                            #'x_kgrs_11364': line.product_tmpl_id.adr_idnumonu.adr_category_id.x_kgrs_11364
                        })
                        
                        if not line.product_tmpl_id.adr_idnumonu.exe22315 and not line.product_tmpl_id.adr_idnumonu.qty_limit > 0:
                            exe11363_total_weight = exe11363_total_weight + line.product_tmpl_id.adr_weight_x_kgrs_11363*line.product_qty
                            exe11364_total_weight = exe11364_total_weight + line.product_tmpl_id.adr_weight_x_kgrs_11364*line.product_qty
                            ## Guardamos las categorías diferentes
                            if not line.product_tmpl_id.adr_idnumonu.adr_category_id.id in categories_ids:
                                categories_ids.append(line.product_tmpl_id.adr_idnumonu.adr_category_id.id)
                        else:
                            if line.product_tmpl_id.adr_idnumonu.exe22315 and not line.product_tmpl_id.adr_idnumonu.qty_limit > 0:
                                exe22315_total_weight = exe22315_total_weight + line.product_tmpl_id.weight*line.product_qty
                                counter_22315 = counter_22315 + 1
                            else:
                                lq_total_weight = lq_total_weight + line.product_tmpl_id.weight*line.product_qty
                                counter_lq = counter_lq + 1

        if len(categories_ids) > 1:
            exention_type = '1.1.3.6.3'
            # Saco el máximo igualmente por no ponerlo directamente igual a 1000. Así al menos es modificable.
            category_obj = self.env['adr.code.category'].browse(categories_ids[0])
            category_max_weight = category_obj.max_weight_11363
            regular_total_weight = exe11363_total_weight
        else:
            if len(categories_ids) == 1:
                exention_type = '1.1.3.6.4'
                category_obj = self.env['adr.code.category'].browse(categories_ids[0])
                category_max_weight = category_obj.max_weight_11364
                regular_total_weight = exe11364_total_weight

        company_data = {
            'logo_web': self.env.user.company_id.logo_web,
            'company_name': self.env.user.company_id.name,
            'street': self.env.user.company_id.street,
            'street2': self.env.user.company_id.street2,
            'zip': self.env.user.company_id.zip,
            'city': self.env.user.company_id.city,
            'state_id': self.env.user.company_id.state_id.name,
            'country_id': self.env.user.company_id.country_id.name,
            'vat': self.env.user.company_id.vat
        }

        delivery_carrier_data = {
            'name': self.carrier_id.name,
            'street': self.carrier_id.street,
            'street2': self.carrier_id.street2,
            'zip': self.carrier_id.zip,
            'city': self.carrier_id.city,
            'state_id': self.carrier_id.state_id.name,
            'country_id': self.carrier_id.country_id.name,
            'vat': self.carrier_id.vat,
            'vehicle': self.delivery_data
        }

        #Ordeno el listado por orden de venta.

        partner_pickings.sort(key=lambda x: x['origin'], reverse=False)

        docs.append({
            'partners': partners_data,
            'movements': partner_pickings,
            'categories_ids': categories_ids
        })

        data = {
            'ids': adr_picks,
            'model': self._name,
            'form': {
                'origin': self.user_id.name,
                'delivery_carrier_data': delivery_carrier_data,
                'exention_type': exention_type,
                'category_max_weight': category_max_weight,
                'regular_total_weight': regular_total_weight,
                'exe22315_total_weight': exe22315_total_weight,
                'counter_22315': counter_22315,
                'lq_total_weight': lq_total_weight,
                'counter_lq': counter_lq,
                'company_data': company_data,
                'picking_batch': self.name,
                'delivery_date': self.delivery_date
            },
            'docs': docs
        }

        return self.env.ref('stock_delivery_batch.delivery_batch_report').report_action(self, data=data)
        
    @api.multi
    def done(self):
        pickings = self.mapped('picking_ids').filtered(lambda picking: picking.state not in ('cancel', 'done'))
        if any(picking.state not in ('assigned') for picking in pickings):
            raise UserError(_('Some pickings are still waiting for goods. Please check or force their availability before setting this batch to done.'))
        for picking in pickings:
            picking.message_post(
                body="<b>%s:</b> %s <a href=#id=%s&view_type=form&model=stock.picking.batch>%s</a>" % (
                    _("Transferred by"),
                    _("Delivery Batch"),
                    picking.delivery_batch_id.id,
                    picking.delivery_batch_id.name))

        picking_to_backorder = self.env['stock.picking']
        picking_without_qty_done = self.env['stock.picking']
        for picking in pickings:
            if all([x.qty_done == 0.0 for x in picking.move_line_ids]):
                # If no lots when needed, raise error
                picking_type = picking.picking_type_id
                if (picking_type.use_create_lots or picking_type.use_existing_lots):
                    for ml in picking.move_line_ids:
                        if ml.product_id.tracking != 'none':
                            raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                # Check if we need to set some qty done.
                picking_without_qty_done |= picking
            elif picking._check_backorder():
                picking_to_backorder |= picking
            else:
                picking.action_done()
        self.write({'state': 'done'})
        if picking_without_qty_done:
            view = self.env.ref('stock.view_immediate_transfer')
            wiz = self.env['stock.immediate.transfer'].create({
                'pick_ids': [(4, p.id) for p in picking_without_qty_done],
                'pick_to_backorder_ids': [(4, p.id) for p in picking_to_backorder],
            })
            return {
                'name': _('Immediate Transfer?'),
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.delivery.transfer',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'target': 'new',
                'res_id': wiz.id,
                'context': self.env.context,
            }
        if picking_to_backorder:
            return picking_to_backorder.action_generate_backorder_wizard()
        return True


class StockPicking(models.Model):
    _inherit = "stock.picking"

    delivery_batch_id = fields.Many2one(
        'stock.delivery.batch', string='Delivery Batch', states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
        help='Delivery batch associated to this picking', copy=False)
