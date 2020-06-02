# -*- coding: utf-8 -*-
from odoo import api,fields, models
#import datetime

class LoanLine(models.Model):

    _name = 'loan.line'
    _description = 'Líneas de la tabla de amortización del préstamo'

    loan_manager_id = fields.Many2one('loan.manager', ondelete='cascade')

    name = fields.Char(string='Ref')
    fecha = fields.Date(string='Fecha pago')
    mensualidad = fields.Float(string='Pago')
    intereses = fields.Float(string='Intereses')
    cap_amort = fields.Float(string='Cap. amortizado')
    cap_pdte = fields.Float(string='Cap. pendiente')

    nombre_entidad = fields.Many2one('res.bank', related='loan_manager_id.entidad', store = True, readonly=True)
    numero_prestamo = fields.Char('número', related='loan_manager_id.name', store=True, readonly=True)
    company_id = fields.Many2one('res.company', related='loan_manager_id.company_id')

    
    

    
    
    