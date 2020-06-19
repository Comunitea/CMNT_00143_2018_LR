
import datetime
from dateutil.relativedelta import *
from . import Asiento
import numpy as np




# Diccionarios con las cuentas a utilizar en la contabilización
ctas_prestamo = {'AMORTIZACION': '17000XXX', 'GASTO': '66231003', 'PAGO': '170009999'}
ctas_coste_ap = {'AMORTIZACION': '17000YYY', 'GASTO': '66231003'}

# suma n primeros términos renta postapagable de razón (1+i)**-1
a = lambda n,i:(1-(1+i)**(-n))/i

#relación de k-ésimos de tiempo
k = {'ANUAL': 1, 'SEMESTRAL': 2, 'TRIMESTRAL': 4, 'CUATRIMESTRAL': 3, 'BIMESTRAL': 6, 'MENSUAL':12}

# formas de calcular los intereses de los préstamos.
clave = ['360/360','365/360','365/365']

"""
Clase que gestiona modeliza de forma genérica los préstamos. Clase abstracta
"""
class Prestamo:

    def __init__(self, fecha, intervalo, tipo_int, plazo, capital, etiquetas, clavePr, gtoAp, carencia):
        """
        :param fecha: fecha de formalización del préstamo
        :param intervalo:
        :param tipo_int: tipo de interés en tanto por uno en el mismo formato de tiempo que el plazo.\
                Si el plazo es mensual i deber ser mensual, si el plazo es trimestral i debe ser trimestral, ....
        :param plazo: número de periodos en que se va a devolver el préstamo
        :param capital: Importe del préstamo
        :param: clavePr. Para calcular los intereses del préstamo
        :param etiquetas: lista con 2 etiquetas analíticas. Una para la entidad y otra para el número de préstamo.
        :param gtoAp: gasto de apertura del préstamo que se quiere activar en lugar de llevarlo íntegramente a gasto del ejercicio.
        """
        self.intervalo = int(intervalo)
        self.tipo_int = float(tipo_int)
        self.plazo = int(plazo)
        self.capital = float(capital)
        
        self.carencia = int(carencia)

        if isinstance(fecha,datetime.datetime):
            self.fecha=fecha
        else:
            self.fecha = datetime.datetime.strptime(fecha, "%d-%m-%Y")

        self.etiquetas = etiquetas
        self.clavePr = clavePr
        self.cuotas = []
        self.gtoAp=gtoAp


    def TRI(self):
        """
        Función para calcular el interés efectivo del préstamo
        referido al k-ésimo de tiempo de las cuotas del préstamo.
        Para obtener el interés efectivo anual hay que multiplicar este valor
        por el k-ésimo de tiempo asociado a este préstamo.
        :return:
        """
        # Lista con los cash flows de cada periodo
        cf=[x.mensualidad for x in self.cuotas]
        #El primero es el desembolso inicial.
        cf[0]=(self.capital-self.gtoAp)*-1

        return np.irr(cf)

    def calcularCosteAmortizado(self):
        """
        Método que calcula la periodificación de los gastos de apertura en las distintas cuotas.
        :return: void
        """
        tri = self.TRI()
        suma = 0
        for c in self.cuotas:
            pos = self.cuotas.index(c)
            if pos == 0:
                c.cap_pdte_ef = self.capital-self.gtoAp
                c.interes_ef = 0
                c.cap_amort_ef = 0
                c.gto_ap_per = 0
            else:
                if pos < len(self.cuotas)-1:
                    c.interes_ef = round(self.cuotas[pos-1].cap_pdte_ef*tri, 2)
                    c.cap_amort_ef = round(c.mensualidad-c.interes_ef, 2)
                    c.cap_pdte_ef = round(self.cuotas[pos-1].cap_pdte_ef-c.cap_amort_ef, 2)
                    c.gto_ap_per = round(c.interes_ef-c.intereses, 2)
                    suma += c.gto_ap_per
                else:
                    c.gto_ap_per=self.gtoAp-suma


    def contabilizarConcesionPrestamo(self):
        """
        Método para contabilizar la concesión del préstamo
        :return:
        """

        asPr = Asiento()

        pr = Apunte(self.fecha, ctas_prestamo['AMORTIZACION'], self.capital * -1, self.etiquetas)
        cbr = Apunte(self.fecha, ctas_prestamo['PAGO'], self.capital - self.gtoAp , self.etiquetas)

        asPr.apuntes.append(pr)
        asPr.apuntes.append(cbr)

        # Si queremos periodificar los gastos de apertura del préstamo
        if self.gtoAp>0:
            gtoPer= Apunte(self.fecha, ctas_coste_ap['AMORTIZACION'], self.gtoAp, self.etiquetas)
            asPr.apuntes.append(gtoPer)

        self.cuotas[0].asiento = asPr

    def contabilizarCuotas(self):
        """
        Método para contabilizar las cuotas de amortización del préstamo. Tanto los pagos como las
        imputaciones a resultados del gasto de apertura periodificado.
        :return:
        """
        # Contabilización de las cuotas del préstamo
        for cuota in self.cuotas:
            if self.cuotas.index(cuota) > 0:
                cuota.contabilizar()
                if self.gtoAp > 0:
                    cuota.contabilizarCosteAmortizado()


    def recalcularCuotas(self, pos, i_k_act):
        """
        Utilidad para préstamos a tipo variable.
        Método para recalcular las cuotas del préstamo a partir de una determinada fecha
        :param pos: posición a partir de la cual vamos a aplicar las nuevas condiciones. Necesitamos saber cual es el capital pendiente
        a partir del cual recalcular el préstamo. pos sería el índice de la última cuota pagada. Allí estará el capital pendiente de amortizar.
        :i_k_act: es el nuevo tipo de interés que se va a aplicar a los periodos que aun no están vencidos.
        :return Un prestamo temporal que contendrá las nuevas cuotas. Debería hacerse un update de las cuotas del préstamo original desde pos+ (i>0)
        """
        #fecha, intervalo, tipo_int, plazo, capital, etiquetas, clavePr, gtoAp

        tmp =None
        #Datos del nuevo préstamo
        tipo_int=i_k_act
        fecha=self.cuotas[pos].fecha
        capital=self.cuotas[pos].cap_pdte
        intervalo=self.intervalo
        plazo=(len(self.cuotas)-1) - pos # -1 por la cuota 0
        etiquetas=self.etiquetas
        clavePr=self.clavePr

        if self.cuotas[pos].cap_pdte_ef > 0: # si estamos periodificando los gastos de apertura
            gtoAp = self.cuotas[pos].cap_pdte-self.cuotas[pos].cap_pdte_ef
        else:
            gtoAp = 0

        if isinstance(self, MensualidadCte):
            tmp = MensualidadCte( fecha, intervalo, tipo_int, plazo, capital, etiquetas, clavePr, gtoAp)
        elif isinstance(self, CuotaAmortizCte):
            tmp = CuotaAmortizCte( fecha, intervalo, tipo_int, plazo, capital, etiquetas, clavePr, gtoAp)
        else:
            print("¿?")

        return tmp

    def calcular(self):
        """
        Implementación en las subclases
        """
        pass

    def __str__(self):
        aux = ""

        for etq in etiquetas:
            aux+= etq + " | "
        aux=aux[:len(aux)-2]+"\n"

        aux += self.clavePr+"\n"

        if isinstance(self, MensualidadCte):
            aux += "Préstamo de mensualidad constante\n"
        elif isinstance(self, CuotaAmortizCte):
            aux += "Préstamo de cuota de amortización constante\n"
        else:
            aux += "¿?"

        aux += "pos;fcha;mens;int;capAm;capPdte\n"
        for c in self.cuotas:
            aux += str(self.cuotas.index(c))+";"
            aux += datetime.datetime.strftime(c.fecha,'%d-%m-%Y')+";"
            aux += '{0:.2f}'.format(c.mensualidad).replace(".", ",")+";"
            aux += '{0:.2f}'.format(c.intereses).replace(".", ",") + ";"
            aux += '{0:.2f}'.format(c.cap_amort).replace(".", ",") + ";"
            aux += '{0:.2f}'.format(c.cap_pdte).replace(".", ",")+";"

            if self.gtoAp > 0:
                aux+='{0:.2f}'.format(c.gto_ap_per).replace(".", ",")

            aux += "\n"
        aux += "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
        aux += "+++++++++++ CONTABILIZACIÓN CUOTAS PRÉSTAMO ++++++++++++++++++++\n"
        aux += "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
        for c in self.cuotas:
            if c.asiento:
                aux += str(c.asiento)

        if self.gtoAp > 0:
            aux += "\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
            aux += "+++++++ CONTABILIZACIÓN PERIODIFICACIÓN GASTOS APERTURA ++++++++\n"
            aux += "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n"
            for c in self.cuotas:
                if c.asiento_ef:
                    aux += str(c.asiento_ef)


        return aux
"""
Clase que modeliza los préstamos de mesnualidad constante (sistema francés).
"""
class MensualidadCte(Prestamo):

    def __init__(self, fecha, intervalo, tipo_int, plazo, capital, etiquetas,clavePr, gtoAp=0,carencia=0):
        Prestamo.__init__(self,fecha,intervalo,tipo_int,plazo,capital,etiquetas,clavePr,gtoAp, carencia)
        self.calcular()


    def calcular(self):

        plazo_amortizacion = self.plazo - self.carencia

        mensualidad = self.capital / a(plazo_amortizacion, self.tipo_int)

        for i in range(self.plazo+1):

            if i == 0:

                fechaC = self.fecha
                mensual = 0
                interes = 0
                capAm = 0
                capPdte = self.capital

            elif i <= self.carencia:
                # Tratamiento de un periodo de carencia
                # Fecha del periodo
                fechaC = self.cuotas[i - 1].fecha + relativedelta(months=+self.intervalo) + relativedelta(day=self.fecha.day)
                # Cálculo de los intereses del periodo
                if(self.clavePr == clave[1]):
                    # Clave [365/360]
                    dif = (fechaC - self.cuotas[i - 1].fecha).days
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int * ( dif / (self.intervalo * 30)), 2)
                else:
                    # Clave [360/360] o [365/365]
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int, 2)
                # La mensualidad son los intereses porque sólo pagamos los intereses
                mensual = interes
                # No se amortiza ningún capital
                capAm = 0
                # Entonces, seguimos con el mismo capital pendiente
                capPdte = round(self.cuotas[i - 1].cap_pdte - capAm,2)

            else:
                # fecha cuota anterior + intervalo de pago +   mismo día de pago que la fecha del préstamo
                fechaC = self.cuotas[i - 1].fecha + relativedelta(months=+self.intervalo) + relativedelta(day=self.fecha.day)

                if(self.clavePr == clave[1]):
                    dif = (fechaC - self.cuotas[i - 1].fecha).days
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int * (dif / (self.intervalo * 30)), 2)
                else:
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int, 2)

                if i < self.plazo:
                    mensual = round(mensualidad,2)
                    capAm = round(mensual-interes,2)
                else:
                    capAm =  round(self.cuotas[i-1].cap_pdte,2)
                    mensual = round(capAm + interes, 2)
                capPdte = round(self.cuotas[i - 1].cap_pdte - capAm,2)

            cuota = Cuota(fechaC,mensual,interes,capAm,capPdte,self.etiquetas)

            self.cuotas.append(cuota)




"""
Clase que modeliza los préstamos con cuota de amortización constante, por tanto, de mensualidad variable.
"""
class CuotaAmortizCte(Prestamo):

    def __init__(self, fecha, intervalo, tipo_int, plazo, capital, etiquetas, clavePr, gtoAp=0, carencia=0):
        Prestamo.__init__(self,fecha,intervalo,tipo_int,plazo,capital,etiquetas,clavePr,gtoAp, carencia)
        self.calcular()

    def calcular(self):

        plazo_amortizacion = self.plazo - self.carencia    
        amortizacion=round(self.capital/float(plazo_amortizacion), 2)

        for i in range(self.plazo+1):

            

            if i == 0:
                fechaC = self.fecha
                mensual = 0
                interes = 0
                capAm = 0
                capPdte = self.capital

            elif i <= self.carencia:
                # Tratamiento de un periodo de carencia
                # Fecha del periodo
                fechaC = self.cuotas[i - 1].fecha + relativedelta(months=+self.intervalo) + relativedelta(day=self.fecha.day)
                # Cálculo de los intereses del periodo
                if(self.clavePr == clave[1]):
                    # Clave [365/360]
                    dif = (fechaC - self.cuotas[i - 1].fecha).days
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int * (dif / (self.intervalo * 30)), 2)
                else:
                    # Clave [360/360] o [365/365]
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int, 2)
                # La mensualidad son los intereses porque sólo pagamos los intereses
                mensual = interes
                # No se amortiza ningún capital
                capAm = 0
                # Entonces, seguimos con el mismo capital pendiente
                capPdte = round(self.cuotas[i - 1].cap_pdte - capAm,2)
                
            else:
                fechaC = self.cuotas[i - 1].fecha + relativedelta(months=+self.intervalo) + relativedelta(day=self.fecha.day)
                if self.clavePr == clave[1]:
                    dif = (fechaC - self.cuotas[i - 1].fecha).days
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int * (dif / (self.intervalo * 30)), 2)
                else:
                    interes = round(self.cuotas[i - 1].cap_pdte * self.tipo_int, 2)

                if i < self.plazo:
                    capAm = amortizacion
                    mensual = round(capAm+interes, 2)

                else:
                    capAm = self.cuotas[i - 1].cap_pdte
                    mensual = round(capAm+interes,2)

                capPdte = self.cuotas[i - 1].cap_pdte - capAm

            cuota = Cuota(fechaC,mensual,interes,capAm,capPdte,self.etiquetas)

            self.cuotas.append(cuota)


"""
Clase utilizada para gestionar cada cuota del préstamo
"""
class Cuota:

    def __init__(self, fecha, mensualidad, intereses, cap_amort, cap_pdte, etiquetas):
        self.fecha = fecha
        self.mensualidad = mensualidad
        self.intereses = intereses
        self.cap_amort = cap_amort
        self.cap_pdte = cap_pdte
        self.etiquetas=etiquetas
        self.asiento=None

        # para coste amortizado
        self.cap_pdte_ef=0
        self.interes_ef=0
        self.cap_amort_ef=0
        self.gto_ap_per=0
        self.asiento_ef=None

    def contabilizar(self):
        """
        Método que contabiliza las cuotas del préstamo
        :return: void
        """
        self.asiento=Asiento()

        apAM=Apunte(self.fecha, ctas_prestamo['AMORTIZACION'], self.cap_amort,self.etiquetas)
        apGto = Apunte(self.fecha, ctas_prestamo['GASTO'], self.intereses, self.etiquetas)
        apPago = Apunte(self.fecha, ctas_prestamo['PAGO'], self.mensualidad*-1, self.etiquetas)

        self.asiento.apuntes.append(apAM)
        self.asiento.apuntes.append(apGto)
        self.asiento.apuntes.append(apPago)

    def contabilizarCosteAmortizado(self):
        """
        Método que contabiliza la periodificación de los gastos de apertura en las distintas cuotas.
        :return: void
        """
        if self.gto_ap_per>0:
            self.asiento_ef=Asiento()
            apGtoEf = Apunte(self.fecha,ctas_coste_ap['GASTO'],self.gto_ap_per,"")
            apAmEf = Apunte(self.fecha,ctas_coste_ap['AMORTIZACION'],self.gto_ap_per*-1,"")
            self.asiento_ef.apuntes.append(apGtoEf)
            self.asiento_ef.apuntes.append(apAmEf)

"""
PRUEBAS0.0125
"""
if __name__ == "__main__":

    # EJEMPLOS

    """
    DATOS PRÉSTAMO
    """
    capital=200000
    iAnual=0.01 # tanto por uno anual.
    k_esimo=k['MENSUAL'] #Amortización mensual
    gtosApertura= 2000
    periodo = 48  # en misma unidad que k-esimo
    #El interés y el plazo deben estar referenciados al mismo periodo de tiempo. En este caso meses
    i_k=iAnual/k_esimo

    intervalo=12/k_esimo # para calcular los vencimientos de las cueotas.
    etiquetas=['PRESTAMO','PASTOR','123456'] # Operación, entidad, número de préstamo

    #PRÉSTAMO MENSUALIDAD CONSTANTE -- [360/360]

    pr=MensualidadCte('15-05-2019', intervalo, i_k, periodo, capital, etiquetas, clave[0], gtosApertura)
    if pr.gtoAp > 0:
        pr.calcularCosteAmortizado()
    pr.contabilizarConcesionPrestamo()
    pr.contabilizarCuotas()
    print(str(pr))
    print(pr.TRI()*k_esimo)

    # Una vez pagada la cuota número 12 el banco modifica el tipo de interés al 2% anual.
    n_ik=0.02/k['MENSUAL']
    tmp = pr.recalcularCuotas(12,n_ik)
    if tmp.gtoAp>0:
        tmp.calcularCosteAmortizado()
    tmp.contabilizarCuotas()

    print("++++++++++++ NUEVAS CONDICIONES ++++++++++++++++++")
    print(str(tmp))
    print("++++++++++++ FIN NUEVAS CONDICIONES ++++++++++++++")

    print("++++++++++++++ PRÉSTAMO CUOTA AMORTIZACIÓN CONSTANTE +++++++++++")

    # PRÉSTAMO CUOTA AMORTIZACIÓN CONSTANTE -- [360/360}
    pr1=CuotaAmortizCte('15-05-2019', intervalo, i_k, periodo, capital, etiquetas, clave[0], gtosApertura)
    if pr1.gtoAp > 0:
        pr1.calcularCosteAmortizado()

    pr1.contabilizarConcesionPrestamo()
    pr1.contabilizarCuotas()

    print(str(pr1))
    print(pr1.TRI()*k_esimo)

    # Una vez pagada la cuota número 12 el banco modifica el tipo de interés al 2% anual.
    n_ik=0.02/k['MENSUAL']
    tmp1 = pr1.recalcularCuotas(12,n_ik)
    if tmp1.gtoAp > 0:
        tmp1.calcularCosteAmortizado()
    tmp1.contabilizarCuotas()

    print("++++++++++++ NUEVAS CONDICIONES ++++++++++++++++++")
    print(str(tmp1))
    print("++++++++++++ FIN NUEVAS CONDICIONES ++++++++++++++")



