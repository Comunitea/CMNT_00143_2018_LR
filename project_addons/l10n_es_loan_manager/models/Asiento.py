import datetime

class Asiento:

    def __init__(self):
        self.apuntes=[]

    def __str__(self):
        aux = ""
        for apunte in self.apuntes:
            aux += str(apunte)+"\n"
        return aux
class Apunte:
    def __init__(self, fchaVto, cuenta, importe, etiquetas):
        self.fchaVto = fchaVto
        self.cuenta = cuenta
        self.importe = importe
        self.etiquetas = etiquetas

    def __str__(self):
        aux = ""
        aux+=datetime.datetime.strftime(self.fchaVto,'%d-%m-%Y')+";"
        aux += self.cuenta+";"
        for etq in self.etiquetas:
            aux += etq+" - "

        aux=aux[:len(aux)-2]+";"

        aux += '{0:.2f}'.format((self.importe if self.importe >= 0 else 0)).replace(".", ",")+";"
        aux += '{0:.2f}'.format((abs(self.importe) if self.importe < 0 else 0)).replace(".", ",")+";"

        return aux
