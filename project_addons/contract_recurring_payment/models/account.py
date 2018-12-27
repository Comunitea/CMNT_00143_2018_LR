from odoo import fields, models


class AccountMove(models.Model):
    _inherit = 'account.move'

    # Campo inverso para asociar account.move con account.voucher
    # Así a la hora de agrupar recibos podremos diferenciar los apuntes
    # cuyo asiento proviene de recibo.
    # Será un one2many con un solo recibo
    voucher_ids = fields.One2many('account.voucher', 'move_id', 'Vouchers')

