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
        return res
        ic_so = self.sudo().env['sale.order'].search([('auto_purchase_order_id', 'in', ic_po.ids)])
        if ic_so:
            for so in ic_so:
                ic_user = so.company_id.intercompany_user_id.id
                ic_company = so.company_id.id
                ctx = self._context.copy()
                ctx.update(force_company=ic_company)
                ic_so.with_context(ctx).sudo(ic_user).action_confirm()
        return res

    def create(self, vals):
        return super().create(vals)


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



