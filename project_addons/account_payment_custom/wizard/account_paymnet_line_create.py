# © 2018 Comunitea
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import models, fields, api
from odoo.osv import expression


class AccountPaymentLineCreate(models.TransientModel):
    _inherit = 'account.payment.line.create'
    _description = 'Wizard to create payment lines'

    start_due_date = fields.Date(string="From Due Date")

    @api.multi
    def _prepare_move_line_domain(self):
        """
        Este método ya devuelve el domain permitiendo negativos,
        sin la condicíon de (debit/credit, >, 0).
        Se permite filtrar los efectos por fecha de inicio también, con lo
        que se reordena el domain de búsqueda. Pero como la fecha de inicio
        no debe aplicarse para los efectos de rectificativas, hay que
        desdoblar el domain en 2, uno con los efectos positivos sin fecha,
        o con fecha en rango, y otro con los negativos sin fecha o hasta la
        fecha dada.
        """
        domain = super(AccountPaymentLineCreate, self).\
            _prepare_move_line_domain()

        domain2 = domain.copy()  # Copia domain para buscar los negativos

        if ('date_maturity', '=', False) in domain and self.start_due_date:
            # Modifico el dominio para que los encuentre  efectos sin fecha
            # o cuyo vencimiento esté en el rango. Lo reordeno para que
            # sea sin fecha o con fecha en rango
            indx = domain.index(('date_maturity', '=', False))
            t1 = domain.pop(indx)  # date_maturyty = False
            t2 = domain.pop(indx - 1)  # date_maturyty <= X
            t3 = ('date_maturity', '>=', self.start_due_date)
            domain.insert(indx-1, t1)
            domain.insert(indx, t2)
            domain.insert(indx+1, t3)

            if self.allow_negative:
                # Vuelvo a añadir la condición de solo efectos positivos, para
                # el domain 1, y la de solo negativos para el domain 2
                if self.order_id.payment_type == 'outbound':
                    domain.append(('credit', '>', 0))
                    domain2.append(('credit', '<=', 0))
                elif self.order_id.payment_type == 'inbound':
                    domain.append(('debit', '>', 0))
                    domain2.append(('debit', '<=', 0))

                # Obtengo los domains normalizados para poder aplicar el OR
                d1 = expression.normalize_domain(domain)
                d2 = expression.normalize_domain(domain2)
                domain = expression.OR([d1, d2])
        return domain

    @api.onchange(
        'date_type', 'move_date', 'due_date', 'start_due_date',
        'journal_ids', 'invoice',
        'target_move', 'allow_blocked', 'payment_mode', 'allow_negative')
    def move_line_filters_change(self):
        res = super(AccountPaymentLineCreate, self).move_line_filters_change()
        return res
