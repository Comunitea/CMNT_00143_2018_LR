# -*- coding: utf-8 -*-
from odoo import api,fields, models
from odoo.exceptions import UserError
from . import Prestamo
import datetime

class LoanManager(models.Model):

    _name = 'loan.manager'
    _description = 'Gestor de préstamos'

    inherit = ['account.journal']

    # Cálculo de i_k
    @api.depends('iAnual','k')
    def calc_ik(self):
        self.i_k = self.iAnual if float(self.k)==0 else float(self.iAnual)/float(self.k) 

    def _default_company(self):
        force_company = self._context.get('force_company')
        if not force_company:
            return self.env.user.company_id.id
        return force_company

    # Número del préstamo
    journal_id = fields.Many2one('account.journal', string="Cuenta bancaria", domain="[('type', '=', 'bank')]", context="{'default_type': 'bank'}", required=True)
    entidad = fields.Many2one('res.bank', string="Entidad", related='journal_id.bank_id', readonly=True, store=True)
    name = fields.Char('Número de préstamo', required=True)
    # Entidad con la que se contrata el préstamo
    #entidad = fields.Char('Entidad', required=True)
    # Tipo de préstamo: mensualidad constante (sistema francés) o cuota de amortización constante, por tanto, mensualidades variables.
    tipo_prestamo = fields.Selection(string='Tipo préstamo', selection=[(0, 'Mensualidad constante'),\
         (1, 'Amortización constante')], default=0)
    # Fecha en que se firma la operación
    fecha_firma = fields.Date(string='Fecha firma', required = True, default=fields.Date.today())
    # Importe del préstamo
    nominal = fields.Float(string='Nominal', required = True)
    # Coste de apertura. Sólo si vamos a contabilizarlo a coste amortizado, es decir, registrando el gasto a lo largo
    # de la vida del préstamo (según el TRI del préstamo).
    coste_apertura =fields.Float(string='Coste apertura', required = True)
    # A la hora de calcular los intereses pueden:
    # 360/360 - Utilizan el año comercial en numerador y denominador.
    # 365/365 - Utilizan el año natural tanto en numerador como en denominador.
    # 365/360 - Los intereses son más elevados porque en el numerador utilizan el año natural y en el denominador el año comercial.
    ratio = fields.Selection(string='Ratio', selection=[('0', '360/360'), ('1', '365/360'), ('2', '365/365')], default='0')
    # Siempre en tanto por uno.
    iAnual = fields.Float(string='iAnual', digits=(1,4), required = True)
    # Campo calculado que pone en la misma unidad de tiempo el tipo de interés que en la frecuencia de pago del préstamo
    # mensual, bimestral, trimestrasl, cuatrimestral, semestral, anual.
    i_k = fields.Float(compute = calc_ik, digits=(1,10), store=False)
    # Número de periodos en meseses, bimestres, trimestres, cuatrimestres, semestres o años en que se va a devolver el préstamo.
    plazo = fields.Integer(string='Plazo total', required = True)
    carencia = fields.Integer(string="Plazo carencia", required=True, default=0)
    k = fields.Selection(string='k-esimo', selection=[(1, 'ANUAL'), (2, 'SEMESTRAL'), (4,'TRIMESTRAL'), (3,'CUATRIMESTRAL')\
        , (6,'BIMESTRAL'), (12,'MENSUAL')], default=12)
    # Dónde almacenamos el préstamo.
    lineas_prestamo = fields.One2many('loan.line', 'loan_manager_id',String="Pagos")
    company_id = fields.Many2one(
        'res.company',
        required=True,
        default=_default_company,
        readonly=True,
    )
    
    #account_journal_id = fields.Many2one('account.journal', 'account.journal.name')

    def check_values(self):
        if self.nominal<0:
            raise UserError("El nominal tiene que ser positivo.")
        if self.coste_apertura<0:
            raise UserError("El coste de apertura tiene que ser positivo.")
        if self.coste_apertura < 0:
            raise UserError("El coste de apertura tiene que ser mayor o igual que 0.") 
        if self.coste_apertura>=self.nominal:
            raise UserError("Revisa los valores de nominal y de coste de apertura.")
        if self.tipo_prestamo is None:
            raise UserError("Debe seleccionar un tipo de préstamo.")  
        if self.ratio is None:
            raise UserError("Debe seleccionar el ratio que van a utilizar a la hora de calcular los intereses.")    
        if self.k is None:
            raise UserError("El plazo del préstamo debe estar referenciado a una unidad de tiempo.")  
        if self.iAnual > 1:
            raise UserError("El tipo de interés tiene que estar en tanto por uno.")  
        if self.iAnual <= 0:
            raise UserError("El tipo de interés tiene que ser mayor que 0.")
        if self.plazo<0:
            raise UserError("El plazo de cancelación del préstamo tiene que ser positivo.")
        if self.carencia<0:
            raise UserError("El plazo de carencia tiene que ser positivo.")
        if self.carencia>self.plazo:
            raise UserError("El plazo de carencia debe ser inferior a la duranción total del préstamo.")
        if len(self.lineas_prestamo)>0:
            raise UserError("Ya has calculado el cuadro de amortización de este préstamo.")    

    # Cálculo del cuadro de amortización del préstamo según los datos anteriores.
    @api.multi
    def calcular_cuadro(self):
        
        # A arreglar ###
        etiquetas =[]
        etiquetas.append(self.entidad)
        etiquetas.append(self.name)
        # ##############

        self.check_values()

        intervalo = 12/self.k
        fecha = fields.Date.from_string(self.fecha_firma).strftime('%d-%m-%Y')
        p_ratio = dict(self._fields['ratio'].selection).get(self.ratio)
        
        if self.tipo_prestamo == 0:
            pr=Prestamo.MensualidadCte(fecha, intervalo, self.i_k, self.plazo, self.nominal, etiquetas, p_ratio, self.coste_apertura, self.carencia)
        elif self.tipo_prestamo == 1:
            pr=Prestamo.CuotaAmortizCte(fecha, intervalo, self.i_k, self.plazo, self.nominal, etiquetas, p_ratio, self.coste_apertura, self.carencia)

        if pr: 
            pr.calcular
            pos=-1
            cuadro = []
            for c in pr.cuotas:
                pos += 1
                cuadro.append((0,0,{'name':str(pos), 'fecha': c.fecha, 'mensualidad': c.mensualidad, 
                'intereses': c.intereses, 'cap_amort': c.cap_amort, 'cap_pdte':c.cap_pdte}))

            self.lineas_prestamo =  cuadro    
        
    
    

    

    
    