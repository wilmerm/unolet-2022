"""
Módulo para el manejo de fechas.
"""

import datetime

try:
    from django.utils.translation import gettext as _
except (ImportError):
    _ = lambda x: x




DIARIO = "DIARIO"
INTERDIARIO = "INTERDIARIO"
SEMANAL = "SEMANAL"
QUINCENAL = "QUINCENAL"
MENSUAL = "MENSUAL"
BIMESTRAL = "BIMESTRAL"
CUATRIMESTRAL = "CUATRIMESTRAL"
SEMESTRAL = "SEMESTRAL"
ANUAL = "ANUAL"

PERIODO_CHOICES = (
    (DIARIO, _("Diario")),
    (INTERDIARIO, _("Interdiario")),
    (SEMANAL, _("Semanal")),
    (QUINCENAL, _("Quincenal")),
    (MENSUAL, _("Mensual")),
    (BIMESTRAL, _("Bimestral")),
    (CUATRIMESTRAL, _("Cuatrimestral")),
    (SEMESTRAL, _("Semestral")),
    (ANUAL, _("Anual")),
)






class Fecha(object):
    """
    Clase para el manejo de fechas.
    """

    @classmethod
    def CompararFechas(self, fecha1, fecha2, operator="=="):
        """
        Realiza la operación de comparación de las dos fechas indicadas de
        acuerdo al operador de comparación indicado.
        """
        try:
            fecha1.year
            fecha2.year
        except AttributeError as e:
            raise ValueError("Las fechas indicadas deben ser objetos de fechas válida en python.")
        # Si una o ambas fechas es un objeto datetime.date no (datetime.datetime)
        # la otra fecha se pasará a date.
        if (isinstance(fecha1, datetime.date) or (isinstance(fecha2, datetime.date))):
            fecha1 = datetime.date(fecha1.year, fecha1.month, fecha1.day)
            fecha2 = datetime.date(fecha2.year, fecha2.month, fecha2.day)
        try:
            fecha1.hours
            fecha2.hours
        except AttributeError as e:
            fecha1 = datetime.date(fecha1.year, fecha1.month, fecha1.day)
            fecha2 = datetime.date(fecha2.year, fecha2.month, fecha2.day)

        if operator in ("==", "="):
            return fecha1 == fecha2
        if operator == "<":
            return fecha1 < fecha2
        if operator in ("<=", "=<"):
            return fecha1 <= fecha2
        if operator == ">":
            return fecha1 > fecha2
        if operator in (">=", "=>"):
            return fecha1 >= fecha2
        if operator in ("!=", "=!", "not"):
            return fecha1 != fecha2

        raise ValueError("El operador '{}' no es válido.".format(operator))

    @classmethod
    def GetTiempo(self, fecha1, fecha2=datetime.date.today(), intexto=False):
        """
        Obtiene la diferencia (tiempo) entre dos fechas.
        """
        try:
            timedelta = fecha2 - fecha1
            days = timedelta.days
            years = int(days / 365)
        except TypeError:
            days = 0
            years = 0
        if intexto == True:
            if years > 0:
                return "{} años".format(years)
            return "{} dias".format(days)
        return days

    @classmethod
    def GetEdad(self, fecha, intexto=False):
        """
        Calcula la edad correspondiente a la fecha indicada.
        Teniendo en cuaenta la fecha actual.
        """
        return self.GetTiempo(fecha1=fecha, intexto=intexto)

    @classmethod
    def GetListadoDeFechas(self, inicio=datetime.date.today(), periodo=MENSUAL, limite=None, fin=None):
        """
        Obtiene un listado con las fechas en el rango dado.

        inicio = fecha de inicio.
        periodo = 'diario' | 'interdiario' | 'semanal' | 'quincenal' | 'mensual' | 'anual'
        limite = cantidad de fechas en el listado.
        fin = fecha límite (opcional).

        Nota: Entre 'limite' y 'fin' se usará el que primero se cumpla. Asi que si se desea
        asegurar que la fecha última sea hasta el 'fin', deberá establecer un limite alto (casi inalcanzable)
        para que le de tiempo a la condición 'fin' cumplirse.
        """
        inicio = datetime.date(inicio.year, inicio.month, inicio.day)
        if not limite:
            limite = 1000000000
        if fin:
            fin = datetime.date(fin.year, fin.month, fin.day)
        periodo = periodo.upper()
        fechas = [inicio]
        fecha = inicio

        if periodo == DIARIO:
            year, month, day = fecha.year, fecha.month, fecha.day
            for i in range(limite):
                fecha = fecha + datetime.timedelta(days=1)
                fechas.append(fecha)
                if (fin):
                    if (fecha >= fin):
                        break
            return fechas

        if periodo == MENSUAL:
            year, month = fecha.year, fecha.month
            for i in range(limite):
                # Se suman los meses, si el mes es el último, entonces se suma un año
                # y se reinicia el mes a 1 nuevamente.
                day = inicio.day
                if month == 12:
                    month = 1
                    year += 1
                else:
                    month += 1
                # Si el día es más alto al maximo del mes, entonces se considera
                # como día el último día del mes.
                for n in range(10):
                    try:
                        fecha = datetime.date(year, month, day)
                    except ValueError:
                        day -= 1
                    else:
                        break
                if (fin) and (fecha > fin):
                    break
                fechas.append(fecha)
            return fechas

    @classmethod
    def GetRangoDeFechas(self, inicio, fin=datetime.date.today(), periodo=MENSUAL):
        """
        Obtiene un listado de todas las fechas comprendidas
        en el rango de fechas indicado.
        """
        return self.GetListadoDeFechas(inicio, periodo, 999999999999, fin)

    @classmethod
    def GetUltimoDiaDelMes(self, year=None, month=None):
        """
        Obtiene el ultimo dia del mes indicado. Si no se indica mes
        se tomará como referencia la fecha actual.
        """
        if not year:
            year = datetime.date.today().year
        if not month:
            month = datetime.date.today().month
        day = 31
        for n in range(10):
            try:
                fecha = datetime.date(year, month, day)
            except ValueError:
                day -= 1
            else:
                break
        return fecha