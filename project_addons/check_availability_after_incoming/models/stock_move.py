# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import json

from odoo import _, api, fields, exceptions, models
from odoo.tools.float_utils import float_compare
from requests import Session

from odoo.modules.registry import Registry

_logger = logging.getLogger(__name__)

try:
    from zeep import Client
    from zeep.transports import Transport
    from zeep.plugins import HistoryPlugin
except (ImportError, IOError) as err:
    _logger.debug(err)

try:
    from odoo.addons.queue_job.job import job
except ImportError:
    _logger.debug('Can not `import queue_job`.')
    import functools

    def empty_decorator_factory(*argv, **kwargs):
        return functools.partial
    job = empty_decorator_factory


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def get_picking_queue_jobs(self):

        self.ensure_one()
        if not self.location_dest_id.check_availability:
            raise ValueError(_('Location check availability is not checked'))
        queues = self.move_lines.mapped('check_availability_jobs_ids')
        action = self.env.ref('queue_job.action_queue_job').read()[0]
        action['domain'] = [('id', 'in', queues.ids)]
        return action


class StockMove(models.Model):
    _inherit = 'stock.move'

    check_availability_jobs_ids = fields.Many2many(
        comodel_name='queue.job', column1='incoming_move_id', column2='job_id',
        string="Connector Jobs", copy=False)

    auto_assigned_move_id = fields.Many2one('stock.move', string="Auto assigned orig move", help='This move give availability for chech availability function')

    @job(default_channel='root.move_check_availability')
    @api.multi
    def process_move_for_check_availability(self):
        self.check_availability_after_incoming()

    def _action_done(self):
        res = super()._action_done()
        if not self.location_dest_id.check_availability:
            return res

        if self.env['ir.config_parameter'].sudo().get_param('delay_check_availability') == 'True':
            res._process_move_for_check_availability()
        else:
            _logger.debug("\n-------\n Búsqueda de disponibilidad JIT.")
            res.check_availability_after_incoming()
        return res

    @api.multi
    def get_moves_to_check(self):
        return self.filtered(lambda x: x.location_dest_id == x.warehouse_id.lot_stock_id or x.location_dest_id in x.warehouse_id.lot_stock_id.child_ids)

    @api.multi
    def _process_move_for_check_availability(self):
        _logger.debug("\n-------\n Añadiendo búsqueda de disponibilidad a la cola.")
        # filtro movimientos que no tengan movimientos de destino
        moves_to_check = self.filtered(lambda x: not x.move_dest_ids and x.location_dest_id.check_availability == True)
        queue_obj = self.env['queue.job'].sudo()
        for move in moves_to_check.get_moves_to_check():
            new_delay = move.sudo(move.create_uid).with_context(
                    company_id=move.company_id.id
                ).with_delay(
                    eta=60,
                ).process_move_for_check_availability()
            job = queue_obj.search([
                    ('uuid', '=', new_delay.uuid)
                ], limit=1)
            job.message_post(body="Se ha creado el nuevo trabajo para el movimiento {}/{} del albaran {}".format(move.id, move.product_id.name, move.picking_id.name))
            move.sudo(move.create_uid).check_availability_jobs_ids |= job


    def get_to_check_availability_domain(self):
        def get_parent(location):
            while location.location_id and location.usage != 'view':
                _logger.info("Ubicación{}".format(location.name))
                location = location.location_id
            return location

        location_id = get_parent(self.location_dest_id)
        _logger.debug("Buscando movimientos con origen en {}".format(location_id.display_name))
        domain = [('company_id', '=', self.company_id.id), ('move_orig_ids', '=', False),
                  ('procure_method', '=', 'make_to_stock'), ('picking_id', '!=', False),
                  ('location_id', 'child_of', location_id.id), ('state', 'in', ('confirmed', 'partially_available')),
                  ('product_id', '=', self.product_id.id)]
        return domain

    @api.multi
    def get_to_check_availability_order(self):

        return self.sorted(key=lambda x: (-eval(x.priority), x.date_expected))


    @api.multi
    def check_availability_after_incoming(self):
        ## todo revisar con varias compañias  ...... ###

        if not self:
            return False
        ctx = self._context.copy()
        company_id = self[0].company_id
        for company_id in self.mapped('company_id'):
            ctx.update(force_company=company_id.id)
            for move in self.filtered(lambda x:x.company_id == company_id):
                user_id = move.create_uid
                move_id = move.sudo(user_id).with_context(ctx)
                domain = move_id.get_to_check_availability_domain()
                moves_to_check = self.env['stock.move'].sudo(user_id).with_context(ctx).search(domain)
                _logger.debug("Movimientos esperando disponibilidad para {} en {}: {}".format(move.product_id.name, move.location_dest_id.name, moves_to_check))
                ordered_moves = moves_to_check.get_to_check_availability_order()
                for o_move in ordered_moves:
                    _logger.debug(
                        "Buscando disponibilidad para  {} en {}: {} del albarán {}".format(o_move.product_id.name,
                                                                                           o_move.location_dest_id.name,
                                                                                           o_move.id,
                                                                                           o_move.picking_id.name))
                    pre_state = o_move.state
                    o_move.with_context(ctx)._action_assign()
                    if o_move.state != pre_state:
                        _logger.info(
                        "Movimiento asignado: {} en {}: {} del albarán {}".format(o_move.product_id.name,
                                                                                           o_move.location_dest_id.name,
                                                                                           o_move.id,
                                                                                           o_move.picking_id.name))
                        o_move.auto_assigned_move_id = move
        return True
