# -*- coding: utf-8 -*-
# © 2019 Comunitea
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo import fields, models, tools, api, _
from odoo.exceptions import AccessError, UserError, ValidationError
from pprint import pprint

class StockBatchPickingSGA(models.Model):

    _inherit = "stock.batch.picking"

    sga_state = fields.Selection ([('NI', 'Sin integracion'),
                                   ('NE', 'No exportado'),
                                   ('PM', 'Pendiente Adaia'),
                                   ('EE', 'Error en exportacion'),
                                   ('EI', 'Error en importacion'),
                                   ('SR', 'Realizado'),
                                   ('SC', 'Cancelado')], 'Estado Adaia', default="NE", track_visibility='onchange', copy=False)

    def button_move_to_done(self):
        return self.move_to_done

    @api.multi
    def move_to_done(self):
        pickings = self.mapped('picking_ids')
        picks = pickings.filtered(lambda x: x.sga_state != 'NI')
        picks.write({'sga_state': 'SR'})
        self.write({'sga_state': 'SR'})


    def button_move_to_NE(self):
        return self.move_to_NE

    @api.multi
    def move_to_NE(self):
        sga_states_to_NE = ('PM', 'EI', 'EE', 'SR', 'SC', False)
        pickings = self.mapped('picking_ids')
        picks = pickings.filtered(lambda x: x.sga_integrated and x.sga_state in sga_states_to_NE)
        self.write({'sga_state': 'NE'})
        picks.write({'sga_state': 'NE'})

    def button_new_adaia_file(self, ctx):
        return self.with_context(ctx).new_adaia_file()

    def new_adaia_file(self, operation=False, force=False):

        ctx = dict(self.env.context)
        if operation:
            ctx['operation'] = operation
        if 'operation' not in ctx:
            ctx['operation'] = 'A'
        pickings = self.mapped('picking_ids')
        picks_in_batch = pickings.filtered(lambda x: x.sga_state == 'NE')
        states_to_check = ('confirmed', 'partially_available')
        states_to_send = 'assigned'
        picks = []
        pick_to_check = picks_in_batch.filtered(lambda x: x.state in states_to_check and not force)
        if pick_to_check and pick_to_check[0]:
            view = self.env.ref('sga_file.stock_adaia_confirm_wizard')
            wiz = self.env['stock.adaia.confirm'].create({'pick_id': pick_to_check.id})
            return {
                'name': 'Confirmación de envio a Adaia',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.adaia.confirm',
                'views': [(view.id, 'form')],
                'view_id': view.id,
                'res_id': wiz.id,
                'target': 'new',
                'context': self.env.context,
            }

        for pick in picks_in_batch.filtered(lambda x: x.state in states_to_send or force):
            if not pick.partner_id:
                raise UserError("No puedes enviar un albarán sin asociarlo a una empresa")

            new_sga_file = self.env['sga.file'].with_context(ctx).\
                check_sga_file('stock.picking', pick.id, pick.picking_type_id.sgavar_file_id.code)
            if new_sga_file:
                picks.append(pick.id)

        if picks:
            self.write({'sga_state': 'PM'})
            self.env['stock.picking'].browse(picks).write({'sga_state': 'PM'})
        else:
            raise ValidationError("No hay albaranes para enviar a Adaia")
        return True
