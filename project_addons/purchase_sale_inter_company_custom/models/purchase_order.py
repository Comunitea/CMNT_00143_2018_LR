# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, api, models

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    from_sale_id = fields.Many2one('sale.order', string="From sale order")

    @api.multi
    def _prepare_sale_order_data(self, name, partner, dest_company,
                                 direct_delivery_address):
        if self.from_sale_id:
            direct_delivery_address = self.from_sale_id.partner_shipping_id
        return super()._prepare_sale_order_data(name=name, partner=partner, dest_company=dest_company,direct_delivery_address=direct_delivery_address)

    @api.multi
    def write_ic_values(self):
        for ic_po in self:
            #lines = ic_po.order_lines
            ic_moves = [('')]



class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    def get_ic_lines(self):
        not_ic_lines = ic_lines = self.env['purchase.order.line']
        for line in self:
            ic_domain = [('auto_purchase_line_id','=', line.id)]
            if self.env['sale.order.line'].search(ic_domain):
                ic_lines |= line
            else:
                not_ic_lines |= line
        return not_ic_lines, ic_lines

    @api.depends('order_id.state', 'move_ids.state', 'move_ids.product_uom_qty', 'sale_line_id.qty_delivered')
    def _compute_qty_received(self):
        not_ic_lines, ic_lines = self.get_ic_lines()
        super(PurchaseOrderLine, not_ic_lines)._compute_qty_received()
        for line in ic_lines:
            line.qty_received = line.sale_line_id.qty_delivered

    @api.depends('order_id.state', 'move_ids.state', 'product_qty')
    def _compute_qty_to_receive(self):

        not_ic_lines, ic_lines = self.get_ic_lines()
        super(PurchaseOrderLine, not_ic_lines)._compute_qty_to_receive()

        for line in ic_lines:
            ic_move_domain = [('sale_line_id.auto_purchase_line_id', '=', line.id), ('location_dest_id.usage', '=', 'customer')]
            move_ids = self.env['stock.move'].sudo().search(ic_move_domain)
            total = 0.0
            for move in move_ids.filtered(
                    lambda m: m.state not in ('cancel', 'done')):
                if move.product_uom != line.product_uom:
                    total += move.product_uom._compute_quantity(
                        move.product_uom_qty, line.product_uom)
                else:
                    total += move.product_uom_qty
            line.qty_to_receive = total