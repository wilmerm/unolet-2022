"""
Módulo para el manejo de préstamos.
"""

from .fecha import *




class Prestamo(Fecha):
    """
    Clase para las operaciones de cálculo de un préstamo.
    """

    def GetDuraccion(self, fecha_inicio, cant_cuotas, periodo=MENSUAL):
        """
        Obtiene el tiempo de duración del préstamo, desde la fecha
        de inicio (desembolso) hasta la fecha en que concluirá según
        la cantidad de cuotas y el periodo en que se generan dichas cuotas.

        ---> (int(years), int(months), int(days))
        """

    def GetAmortizacionCuotaFija(self, monto, tasa, cuotas, periodo=MENSUAL, inicio=datetime.date.today()):
        """
        Args:
            monto (float): monto del préstamo.
            tasa (float): tasa del préstamo.
            cuotas (int): cantidad de cuotas.
            periodo (str): periodo del préstamo (semanal, quincenal, mensual, ...).
            inicio (datetime.date): fecha de inicio del préstamo.

        Returns:
            list: Una lista de dicionarios.
        """
        # Calculamos el valor de la cuota.
        valor, interes, capital_restante = self.GetValorDeCuotaFija(monto, tasa, cuotas, periodo)
        # Obtenemos el listado de cortes.
        fechas = self.GetListadoDeFechas(inicio, periodo, cuotas)
        tabla = []
        # Variables para los totales.
        t_valor, t_interes, t_capital, t_capital_restante = Decimal(), Decimal(), Decimal(), Decimal()

        n = 1 # Número de cuota.
        for fecha in fechas[1:]:
            # Calculamos el interés generado en este corte.
            interes = capital_restante * (tasa / Decimal(100))
            # Calculamos el capital restante.
            capital = valor - interes
            capital_restante -= capital
            # Agregamos el corte al listado.
            tabla.append({
                "cuota": n,
                "fecha": fecha,
                "valor": round(valor, 2),
                "interes": round(interes, 2),
                "capital": round(capital, 2),
                "capital_restante": round(capital_restante, 2),
                "clase": "item",
            })
            # Sumamos el corte a los totales.
            t_valor += valor
            t_interes += interes
            t_capital += capital
            t_capital_restante = capital_restante
            n += 1
        # Agregamos los totales en el último item del listado.
        tabla.append({
            "cuota": "",
            "fecha": "Total",
            "valor": round(t_valor, 2),
            "interes": round(t_interes, 2),
            "capital": round(t_capital, 2),
            "capital_restante": round(t_capital_restante, 2),
            "clase": "total",
        })
        return tabla

    def GetAmortizacionCuotaVariable(self, monto, tasa, cuotas, periodo=MENSUAL, inicio=datetime.date.today()):
        """
        Retorna un listado de diccionarios que contienen
        información de las cuotas de la tabla de amortización
        de un préstamo con cuota de tipo variable.
        """
        capital_restante = monto
        cuotas = cuotas
        tasa = tasa
        periodo = periodo
        fechas = self.GetListadoDeFechas(inicio, periodo, cuotas)
        tabla = []
        capital = capital_restante / cuotas
        t_valor, t_interes, t_capital, t_capital_restante = Decimal(), Decimal(), Decimal(), Decimal()

        n = 1 # Número de cuota.
        for fecha in fechas[1:]:
            interes = (capital_restante / Decimal(100)) * tasa
            valor = capital + interes
            capital_restante = capital_restante - capital

            tabla.append({
                "cuota": n,
                "fecha": fecha,
                "valor": round(valor, 2),
                "interes": round(interes, 2),
                "capital": round(capital, 2),
                "capital_restante": round(capital_restante, 2),
                "clase": "item",
            })
            t_valor += valor
            t_interes += interes
            t_capital += capital
            t_capital_restante = capital_restante
            n += 1
        # Agregamos los totales en el último item.
        tabla.append({
            "cuota": "",
            "fecha": "Total",
            "valor": round(t_valor, 2),
            "interes": round(t_interes, 2),
            "capital": round(t_capital, 2),
            "capital_restante": round(t_capital_restante, 2),
            "clase": "total",
        })
        return tabla

    def GetAmortizacionTitulos(self):
        """
        Obtiene los nombres de las columnas de la tabla de amortización.
        """
        return (_("Cuota"), _("Fecha"), _("Valor"), _("Interés"), _("Capital"), _("Capital restante"))

    def GetComportamientoDePagosCuotaFija(self, monto, tasa, cuotas, interesmora, periodo=MENSUAL, inicio=datetime.date.today(), pagos=[]):
        """
        Obtiene el comportamiento de pagos de un préstamo.
        Los pagos deben ser un listado de tuplas (fecha, montopagado).
        """
        pagos = [[fecha, monto, False] for fecha, monto in pagos]
        comp = []
        # Obtenemos el valor de la cuota del préstamo.
        valor, interes, capital = self.GetValorDeCuotaFija(monto, tasa, cuotas, periodo, limit_dec=2)
        capital_restante = capital
        # La diferencia es el remanente que queda despues de haber pagado de menos o de más,
        # lo cual se va a sumar o restar en el próximo corte según sea el caso.
        diferencia = 0
        # La mora es el valor adicional que se le sumará al monto por pagar en caso de atrasos en el pago.
        mora = 0
        # Indica si la cuota está o no vencida por pago pendiente cuando la fecha de pago pasó.
        vencida = False
        # Obtenemos las fechas en que se generarán las cuotas.
        cortes = self.GetListadoDeFechas(inicio, periodo, limite=cuotas)
        n = 1 # Número de la cuota.
        for corte in cortes[1:]:
            # Obtenemos la sumatoria de todos los pagos realizados en la fecha de corte correspondiente.
            # Asegurandonos de poner istomado en True para evitar que sea tomado en cortes posteriores.
            pagado = 0
            i = 0
            for fecha, pago, istomado in pagos.copy():
                if istomado == False:
                    if fecha <= corte:
                        pagado += pago
                        pagos[i][2] = True
                i += 1
            # Monto a pagar generado en este corte, el cual es igual a la sumatoria del
            # valor de la cuota, más el monto remanente del corte anterior, más el monto por mora si lo hay.
            # el balance a pagar no se reduce por los pagos, este balance queda como prueba que fue el monto
            # que se generó a pagar en este corte, diferente del 'por pagar' que si se reduce con los pagos.
            apagar = valor + diferencia + mora
            # El saldo anterior a favor o en contra, es extraido de la diferencia calculada en el corte anterior.
            saldo_anterior = diferencia
            # La mora cargada en este corte, es extraida del cálculo que se hizo de la mora en el corte anterior.
            mora_cargada = mora

            # Si la fecha de corte pasó:
            if corte < datetime.date.today():
                # Si se realizó el pago completo a lo justo.
                if pagado == apagar:
                    mora = 0
                    vencida = False
                # Si no se realizó pago o no se pago completo.
                # generamos una mora, la cual es equivalente a un porcentaje del valor
                # de la cuota (valor de la cuota sin interés ni otros cargos.)
                elif pagado < apagar:
                    mora = round((valor / 100) * interesmora, 2)
                    vencida = True
                # Si el monto pagado fue mayor a lo que debió pagarse.
                elif pagado > apagar:
                    mora = 0
                    vencida = False
            # Si aún no vence la fecha de pago. Esta fecha aun no ha llegado, por lo cual no
            # es necesario que se pague, asi que no generamos mora ni
            else:
                mora = 0
                vencida = False


            diferencia = apagar - pagado
            # Por pagar es el balance que el cliente tiene pendiente pagar. Este balance es
            # el balance generado a pagar en el corte, restándole el monto que ya se ha pagado.
            # Si por pagar es menor que 0, se establece por pagar igual a 0.
            porpagar = apagar - pagado
            if porpagar < 0:
                porpagar = 0

            interes = round((capital_restante + saldo_anterior) * (tasa / Decimal(100)), 2)
            capital = apagar - interes
            capital_restante -= capital

            # Agregamos el comportamiento de este corte.
            comp.append({
                "corte": corte, # fecha de corte.
                "apagar": apagar, # monto cargado que se deberá pagar.
                "pagado": pagado, # monto que se ha pagado ya en este corte.
                "porpagar": porpagar, # monto por pagar restante en caso de ya haber pagos.
                "mora": mora_cargada, # comisión por mora cargada en caso de atrasos
                "diferencia": diferencia, # Diferencia reflejada entre el valor absoluto de la cuota y el monto a pagar.
                "saldo_anterior": saldo_anterior, # Saldo a favor o en contra que queda del anterior corte.
                "valor": valor, # Valor absoluto de la cuota.
                "interes": interes,
                "capital": capital,
                "capital_restante": capital_restante,
                "cuota": n, # Número de la cuota.
                "vencida": vencida, # Indica si está cuota está o no vencida (bool).
                "clase": {True: "cuotavencida", False: "cuotanormal", None: ""}[vencida], # Clase para usar en style CSS.
            })

            n += 1

        # Una vez que se han cumplido todas las cuotas, pero aún queda
        # saldo pendiente por pagar, se generarán cuotas (solo con el valor adeudado) por
        # cada corte extra cumplido hasta la fecha actual, y su respectiva mora cargada.

        # Obtenemos el último corte del comportamiento, y verificamos que este tenga
        # aún un balance pendiente por pagar.
        last = comp[-1]
        if last["porpagar"] > 0:
            # Generamos los corte desde la fecha del último corte, hasta el día de hoy.
            cortes = self.GetListadoDeFechas(last["corte"], periodo, fin=datetime.date.today())
            # Obtenemos algunas informaciones del último corte.
            apagar = last["apagar"]
            diferencia = last["diferencia"]
            mora = last["mora"]
            # El número de cuota continua donde quedó el último corte.
            n = cuotas + 1
            for corte in cortes[1:]:
                # Obtenemos la suma de los pagos que se realizaron en este corte.
                pagado = 0
                i = 0
                for fecha, pago, istomado in pagos.copy():
                    if istomado == True:
                        continue
                    elif fecha <= corte:
                        pagado += pago
                        pagos[i][2] = True
                    i += 1
                # No se generan más cuotas, sino que se le suma la mora al monto vencido.
                apagar += mora
                mora_cargada = mora
                # Se realiza la comprobación para verificar si se ha pagado el corte
                # completo o parcial, o nada, para determinar si se seguirá generando moras.
                if pagado == apagar:
                    mora = 0
                    vencida = False
                elif pagado < apagar:
                    mora = round((valor / 100) * interesmora, 2)
                    vencida = True
                elif pagado > apagar:
                    mora = 0
                    vencida = False
                # Obtenemos el monto por pagar:
                diferencia = apagar - pagado
                porpagar = apagar - pagado
                if porpagar < 0:
                    porpagar = 0

                interes = round((capital_restante + saldo_anterior) * (tasa / Decimal(100)), 2)
                capital = apagar - interes
                capital_restante -= capital

                # Agregamos la nueva cuota al comportamiento.
                comp.append({
                    "corte": corte, # fecha de corte.
                    "apagar": apagar, # monto cargado que se deberá pagar.
                    "pagado": pagado, # monto que se ha pagado ya en este corte.
                    "porpagar": porpagar, # monto por pagar restante en caso de ya haber pagos.
                    "mora": mora_cargada, # comisión por mora cargada en caso de atrasos
                    "diferencia": diferencia, # Diferencia reflejada entre el valor absoluto de la cuota y el monto a pagar.
                    "saldo_anterior": saldo_anterior, # Saldo a favor o en contra que queda del anterior corte.
                    "valor": valor, # Valor absoluto de la cuota.
                    "interes": interes,
                    "capital": capital,
                    "capital_restante": capital_restante,
                    "cuota": n, # Número de la cuota.
                    "vencida": vencida, # Indica si está cuota está o no vencida (bool).
                    "clase": "cuotavencidaextra", # Clase para usar en style CSS.
                })
                n += 1

        # Estadisticas.
        stat = {}
        stat["cuotas_vencidas"] = len([c for c in comp if c["vencida"]]) # Cantidad de cuotas vencidas.
        # Retornamos los datos en un diccionario.
        return {"comportamiento": comp, "estadisticas": stat}

    def GetProximoPago(self, monto, tasa, cuotas, interesmora, periodo=MENSUAL, inicio=datetime.date.today(), pagos=[]):
        """
        Obtiene la información del próximo pago que deberá realizarce.
        """
        comportamiento = self.GetComportamientoDePagosCuotaFija(monto, tasa, cuotas, interesmora, periodo, inicio, pagos)["comportamiento"]
        for comp in comportamiento:
            # Verificamos la cuota más próxima que aun no se ha pagado en su totalidad.
            if (comp["corte"] >= datetime.date.today()):
                if (comp["pagado"] < comp["apagar"]):
                    return comp

        # Si ya todas las cuotas se han cumplido,
        # pero aun queda balance pendiente.
        comp = comportamiento[-1]
        if comp["porpagar"] > 0:
            return comp

    def GetValorDeCuotaFija(self, monto, tasa, cuotas, periodo=MENSUAL, limit_dec=None):
        """
        Retorna el valor actual de la cuota, según el método francés,
        en donde las cuotas son fijas. -> float(x)

        Formula = R = P [(i (1 + i)**n) / ((1 + i)**n – 1)].
        Donde:
            R = renta (cuota)
            P = principal (préstamo adquirido)
            i = tasa de interés
            n = número de periodos

        -> (Moneda valor, Moneda interes, Moneda monto)
        """
        tasa = tasa / Decimal(100)
        if periodo == DIARIO:
            tasa /= Decimal(30.4167)
        elif periodo == SEMANAL:
            tasa /= Decimal(4.34524)
        if periodo == QUINCENAL:
            tasa /= Decimal(2.0)
        elif periodo == ANUAL:
            tasa *= 12

        # Si no se especifica una tasa, se pone un número casi imperceptible para
        # evitar que la formula lanze una excepción de división por cero.
        if not tasa:
            tasa = Decimal(0.00000000001)
        # Furmula para el cálculo según el sistema francés.
        valor = monto * ( (tasa * ((1 + tasa)**cuotas)) / (((1 + tasa)**cuotas) - 1) )
        interes = valor - monto
        if limit_dec:
            return (round(valor, limit_dec), round(interes, limit_dec), round(monto, limit_dec))
        return (valor, interes, monto)

    def GetValorDeCuotaVariable(self, capital, tasa, periodo=MENSUAL):
        """
        Retorna una tupla con el valor de la cuota, el interes y el capital.
        para prestamos con cuotas variables.
        --> (valor, interes, capital)
        """
        interes = (capital / 100) * tasa
        if periodo == DIARIO:
            interes /= 30.4167
        elif periodo == SEMANAL:
            interes /= 4.34524
        if periodo == QUINCENAL:
            interes /= 2.0
        elif periodo == ANUAL:
            interes *= 12

        valor = capital + interes
        return (valor, interes, capital)