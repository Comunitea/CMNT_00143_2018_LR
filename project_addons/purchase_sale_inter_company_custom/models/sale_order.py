# -*- coding: utf-8 -*-
# © 2019 Comunitea Servicios Tecnológicos S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_default_autoconfirm_ic(self):
        return self.env.user.company_id.auto_confirm_ic_ops

    @api.multi
    def write_ic_values(self):
        for ic_so in self:

            #lines = ic_so.order_lines
            ic_moves = [('')]

    @api.multi
    def action_confirm(self):

        res = super(SaleOrder, self).action_confirm()
        ic_domain = [('from_sale_id', 'in', self.filtered(lambda x:x.company_id.sale_auto_validation).ids)]
        ic_po = self.env['purchase.order'].search(ic_domain)
        if ic_po:
            for po in ic_po:
                ic_user = po.company_id.intercompany_user_id.id
                ic_company = po.company_id.id
                ctx = self._context.copy()
                ctx.update(force_company=ic_company)
                po.with_context(ctx).sudo(ic_user).button_confirm()

            ic_po.write_ic_values()
        return res
        ic_so = self.sudo().env['sale.order'].search([('auto_purchase_order_id', 'in', ic_po.ids)])
        if ic_so:
            for so in ic_so:
                ic_user = so.company_id.intercompany_user_id.id
                ic_company = so.company_id.id
                ctx = self._context.copy()
                ctx.update(force_company=ic_company)
                ic_so.with_context(ctx).sudo(ic_user).action_confirm()


        sol = self.env['sale.order.line']
        so = self.env['sale.order']
        sm = self.env['stock.move']

        for line in self:
            domain = [('ic_sale_line_ic', '=', line.id)]
            ic_pick = sm.sudo().search(domain).picking_id


            self.picking_id.sudo().write({'ic_sale_ids': [(4, self.sudo().ic_sale_line_id.order_id.id)]})
            sql = 'update sale_order_line where ic_sale_line_ic={} set ic'.format(line.id)
            self.env['']
        if self.ic_sale_line_id:
            self.picking_id.sudo().write({'ic_sale_ids': [(4, self.sudo().ic_sale_line_id.order_id.id)]})
        return res


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    ic_move_ids = fields.One2many('stock.move', 'ic_sale_line_id', string='IC Stock Moves')

    @api.multi
    def _get_delivered_qty(self):
        self.ensure_one()
        if self.sudo().ic_move_ids:
            qty = 0.0
            for move in self.sudo().ic_move_ids.filtered(lambda r: r.state == 'done' and not r.scrapped):
                if move.location_dest_id.usage == "customer":
                    if not move.origin_returned_move_id or (move.origin_returned_move_id and move.to_refund):
                        qty += move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)
                elif move.location_dest_id.usage != "customer" and move.to_refund:
                    qty -= move.product_uom._compute_quantity(move.product_uom_qty, self.product_uom)
            return qty
        return super(SaleOrderLine, self.filtered(lambda x: not x.ic_move_ids))._get_delivered_qty()

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        super()

