"""
Reportes genéricos, preconfigurados para su uso.
"""
from django import forms
from django.utils.translation import gettext as _
from django.urls import reverse_lazy

from fuente import var
from fuente.report.base import (Report, ModelReport, ReportDoesNotExist, 
    ReportLocked, Total, TotalFor)
from fuente.report.fields import (TextField, IntegerField, FloatField, 
    DecimalField, DateField, DateTimeField, BooleanField)
from fuente.report.forms import FormSearch

from articulo.models import Articulo
from cliente.models import Person
from contabilidad.models import (Transaccion,)
from documento.models import (Documento, DocumentoTipo, FACTURA_CONTADO, 
    FACTURA_CREDITO, FACTURAS)






# ------------------------------------------------------------------------------
# VENTAS.
# ------------------------------------------------------------------------------


class VentasPorFecha(ModelReport):
    """
    Reporte de ventas por fecha.

    """
    cliente = TextField("cliente", _("Cliente"), "persona.id")

    cliente_nombre = TextField("cliente_nombre", _("Nombre del cliente"), 
    "persona_nombre")

    fecha = DateTimeField("hora", _("Hora"), "create_date", strformat=":%H")

    numero = TextField("numero", _("Número"), "GetNumero")

    venta = DecimalField("venta", _("Venta"), "GetImporteLocal",
    cssclass="text-right", jsfunction="intcomma")

    descuento = DecimalField("descuento", _("Descuento"), "GetDescuentoLocal",
    cssclass="text-right", jsfunction="intcomma")

    itbis = DecimalField("impuesto", _("Impuesto"), "GetImpuestoLocal",
    cssclass="text-right", jsfunction="intcomma")
    
    venta_neta = DecimalField("venta_neta", _("Venta neta"), "GetTotalLocal", 
    cssclass="text-right", jsfunction="intcomma")

    class Meta:
        model = Documento
        title = _("REPORTE DE VENTAS POR FECHA")
        description = _("Reporte de ventas para una fecha específica.")
        img = var.IMG_DOCUMENTO_FACTURA

        # Totales (cada item representa un caja de totales).
        totals = {
            "general": Total(("venta", _("Venta")),
                ("descuento", _("Descuento")), ("itbis", _("Itbis")),
                ("venta_neta", _("Venta neta")), title=_("Total general")),

            "por_tipo": TotalFor(field="tipo.codename", fieldvalue="GetTotalLocal",
                title=_("Total por tipo de documento")),

            "por_condicion": TotalFor(field="tipo.clase",
                fieldvalue="GetTotalLocal", title=_("Total por condición")),
        }

        charts = (
            ("por_tipo", "chart_div1", {}, "BarChart"),
            ("por_condicion", "chart_div2", {}, "PieChart"),
        )

        # Filtro de búsqueda (Utiliza django.forms.fields).
        form_search = FormSearch(rfields=(
            ("fecha", forms.DateField(label=_("Fecha"),
                widget=forms.widgets.DateInput(attrs={"type": "date"}),
                help_text=_("Indique la fecha a generar."))),

            ("a_credito", forms.BooleanField(required=False, label=_("A crédito"),
                help_text=_("Mostrar las ventas a crédito."))),

            ("a_contado", forms.BooleanField(required=False, label=_("A contado"),
                help_text=_("Mostrar las ventas a contado."))),

            ("tipos", forms.ModelMultipleChoiceField(label=_("Tipos"),
                queryset=DocumentoTipo.objects.filter(clase__in=(FACTURA_CONTADO, 
                FACTURA_CREDITO))))
        ))


    def __init__(self, obj, report):
        super().__init__(obj, report)

    @classmethod
    def generate(self, request):
        reporte = super().generate(request)
        fecha = request.GET.get("fecha")
        a_credito = request.GET.get("a_credito")
        a_contado = request.GET.get("a_contado")
        tipos = request.GET.getlist("tipos")

        if not fecha:
            return reporte.none()

        if (not a_credito) and (not a_contado):
            return reporte.none()
        elif (a_credito) and (not a_contado):
            reporte.filter(tipo__clase=var.FACTURA_CREDITO)
        elif (not a_credito) and (a_contado):
            reporte.filter(tipo__clase=var.FACTURA_CONTADO)
        else:
            reporte.filter(tipo__clase__in=(var.FACTURA_CREDITO, 
                var.FACTURA_CONTADO))

        reporte.filter(tipo__in=tipos)
        reporte.filter(fecha=fecha).order_by("create_date")
        reporte.description = _("Fecha: ") + fecha
        return reporte



class VentasPorRangoDeFechas(ModelReport):
    """
    Reporte de ventas en un rango de fechas.

    """
    cliente = TextField("cliente", _("Cliente"), "persona.id")

    cliente_nombre = TextField("cliente_nombre", _("Nombre del cliente"), 
    "persona_nombre")

    fecha = DateTimeField("fecha", _("Fecha"), "fecha", strformat=":%d/%m/%Y")

    numero = TextField("numero", _("Número"), "GetNumero")

    venta = DecimalField("venta", _("Venta"), "GetImporteLocal",
    cssclass="text-right", jsfunction="intcomma")

    descuento = DecimalField("descuento", _("Descuento"), "GetDescuentoLocal",
    cssclass="text-right", jsfunction="intcomma")

    itbis = DecimalField("impuesto", _("Impuesto"), "GetImpuestoLocal",
    cssclass="text-right", jsfunction="intcomma")
    
    venta_neta = DecimalField("venta_neta", _("Venta neta"), "GetTotalLocal", 
    cssclass="text-right", jsfunction="intcomma")

    class Meta:
        model = Documento
        title = _("REPORTE DE VENTAS POR RANGO DE FECHAS")
        description = _("Reporte de ventas para un rango de fechas.")
        img = var.IMG_DOCUMENTO_FACTURA

        # Totales (cada item representa un caja de totales).
        totals = {
            "general": Total(("venta", _("Venta")),
                ("descuento", _("Descuento")), ("itbis", _("Itbis")),
                ("venta_neta", _("Venta neta")), title=_("Total general")),

            "por_tipo": TotalFor(field="tipo.codename", fieldvalue="GetTotalLocal",
                title=_("Total por tipo de documento")),

            "por_condicion": TotalFor(field="tipo.clase",
                fieldvalue="GetTotalLocal", title=_("Total por condición")),
        }

        charts = (
            ("por_tipo", "chart_div1", {}, "BarChart"),
            ("por_condicion", "chart_div2", {}, "PieChart"),
        )

        # Filtro de búsqueda (Utiliza django.forms.fields).
        form_search = FormSearch(rfields=(
            ("fecha1", forms.DateField(label=_("Fecha inicial"),
                widget=forms.widgets.DateInput(attrs={"type": "date"}),
                help_text=_("Indique la fecha inicial a generar."))),

            ("fecha2", forms.DateField(label=_("Fecha final"),
                widget=forms.widgets.DateInput(attrs={"type": "date"}),
                help_text=_("Indique la fecha final a generar."))),

            ("tipos", forms.ModelMultipleChoiceField(label=_("Tipos"),
                queryset=DocumentoTipo.objects.filter(clase__in=(FACTURA_CONTADO, 
                FACTURA_CREDITO)))),

            ("a_credito", forms.BooleanField(required=False, label=_("A crédito"),
                help_text=_("Mostrar las ventas a crédito."))),

            ("a_contado", forms.BooleanField(required=False, label=_("A contado"),
                help_text=_("Mostrar las ventas a contado."))),
        ))

    @classmethod
    def generate(self, request):
        reporte = super().generate(request)
        fecha1 = request.GET.get("fecha1")
        fecha2 = request.GET.get("fecha2")
        a_credito = request.GET.get("a_credito")
        a_contado = request.GET.get("a_contado")
        tipos = request.GET.getlist("tipos")

        if (not fecha1) and (not fecha2):
            return reporte.none()

        if (not a_credito) and (not a_contado):
            return reporte.none()
        elif (a_credito) and (not a_contado):
            reporte.filter(tipo__clase=var.FACTURA_CREDITO)
        elif (not a_credito) and (a_contado):
            reporte.filter(tipo__clase=var.FACTURA_CONTADO)
        else:
            reporte.filter(tipo__clase__in=(var.FACTURA_CREDITO, 
                var.FACTURA_CONTADO))

        reporte.filter(tipo__in=tipos)
        reporte.filter(fecha__range=(fecha1, fecha2)).order_by("fecha")
        reporte.description = _("Rango de fechas: ") + f"({fecha1} - {fecha2})."
        return reporte




class BalanceDeInventario(ModelReport):
    """
    Reporte balance de inventario (disponibilidad y costo de artículos).

    """
    codename = TextField("codename", _("Referencia"), "codename")

    description = TextField("description", _("Descripción"), "description")

    grupo = TextField("grupo", _("Grupo"), "grupo")

    familia = TextField("familia", _("Familia"), "familia")

    disponible = DecimalField("disponible", _("Disponible"), "disponible", 
    cssclass="text-right", jsfunction="intcomma")

    costo = DecimalField("costo", _("Costo"), "costo_promedio", 
    cssclass="text-right", jsfunction="intcomma")


    class Meta:
        model = Articulo
        title = _("REPORTE BALANCE DE INVENTARIO")
        description = _("Reporte de balance de inventario.")
        img = var.IMG_ARTICULO

        # Totales (cada item representa un caja de totales).
        totals = {
            "general": Total(("disponible", _("Disponible")), 
                ("costo_promedio", _("Costo")), title=_("Total general")),

            "por_grupo": TotalFor(field="grupo.codename", fieldvalue="disponible",
                title=_("Total por grupo")),

            "por_familia": TotalFor(field="familia.codename",
                fieldvalue="disponible", title=_("Total por familia")),
        }

        # Filtro de búsqueda (Utiliza django.forms.fields).
        form_search = FormSearch(rfields=(
            ("only_disponible", forms.BooleanField(required=False, 
            label=_("Solo dispnibles"), help_text=_("Mostrar solo los artículos "
            "que tengan disponibilidad."))),
        ))

    @classmethod
    def generate(self, request):
        reporte = super().generate(request)
        only_disponible = request.GET.get("only_disponible")
        if only_disponible:
            reporte.filter(disponible__gt=0)
        return reporte




class BalanceDeClientes(ModelReport):
    """
    Reporte balance de clientes.
    
    """
    id = IntegerField("id", _("Id"), "id")

    identification = TextField("identification", _("Identificación"), 
    "get_identification")

    identification_type = TextField("idnetification_type", _("Tipo ident."), 
    "get_identification_type_display")

    nombre = TextField("nombre", _("Nombre"), "GetFullName")

    balance = DecimalField("balance", _("Balance"), "balance", 
    cssclass="text-right", jsfunction="intcomma")


    class Meta:
        model = Person
        title = _("REPORTE BALANCE DE CLIENTES")
        description = _("Reporte de balance de clientes.")
        img = var.IMG_ARTICULO

        # Totales (cada item representa un caja de totales).
        totals = {
            "balance": Total(("balance", _("Balance")), title=_("Total general")),
        }

    @classmethod
    def generate(self, request):
        reporte = super().generate(request)
        reporte.exclude(balance=0)
        return reporte




class PagosDeClientesDetallado(ModelReport):
    """
    Reporte de pagos de clientes (detallado).
    
    """
    id = IntegerField("id", _("Id"), "id")

    identification = TextField("identification", _("Identificación"), 
    "get_identification")

    identification_type = TextField("idnetification_type", _("Tipo ident."), 
    "get_identification_type_display")

    nombre = TextField("nombre", _("Nombre"), "GetFullName")


    class Meta:
        model = Person
        title = _("REPORTE PAGOS DE CLIENTES (DETALLADO)")
        description = _("Listado de pagos realizados por cada cliente.")
        img = var.IMG_ARTICULO

        # Totales (cada item representa un caja de totales).
        totals = {
            "pagos": Total(("GetPagosSum", _("Total")), title=_("Total de pagos")),
        }

        has_detail = True

    @classmethod
    def generate(self, request):
        reporte = super().generate(request)
        reporte.exclude(balance=0)
        return reporte

    def get_detail(self):
        detail = Pagos.generate(self._report.request)
        detail.filter(documento__persona=self._obj)
        return detail



class Pagos(ModelReport):
    """
    Reporte de pagos realizados por los clientes.
    
    """
    numero = TextField("numero", _("Número"), "GetNumero")

    fecha = DateField("fecha", _("Fecha"), "fecha")

    documento = TextField("documento", _("Documento"), "documento")

    forma_de_pago = TextField("forma_de_pago", _("Forma de pago"), "forma_de_pago")

    monto = DecimalField("monto", _("Monto"), "GetMontoLocal", 
    cssclass="text-right", jsfunction="intcomma", is_column_total=True)


    class Meta:
        model = Transaccion
        title = _("Pagos de clientes")
        description = _("Reporte de pagos realizados por los clientes.")
        img = var.IMG_ARTICULO
        # Totales (cada item representa un caja de totales).
        totals = {
            "monto": Total(("monto", _("Total")), title=_("Total")),
        }

    @classmethod
    def generate(self, request):
        reporte = super().generate(request)
        reporte.filter(tipo="CREDITO")
        return reporte






# ------------------------------------------------------------------------------
# Identificadores únicos para los reportes creados.
# ------------------------------------------------------------------------------
# Estos identificadores servirán para identificar que reporte necesita el
# usuario al pasar el identificador por la URL.

def get_report_class_from_id(report_id):
    """
    Obtiene la clase del reporte que coincida con el id indicado.
    """
    try:
        return ReporteIds.items[int(report_id)][1]
    except (KeyError):
        raise ReportDoesNotExist(f"No existe reporte con el id '{report_id}'.")



class ReporteIds:
    groups = {
        "ventas": {"name": _("Ventas"), "img": var.IMG_DOCUMENTO_FACTURA,
        "color": "#27AE60"},

        "inventario": {"name": _("Inventario"), "img": var.IMG_ARTICULO, 
        "color": "#ffbb00"},

        "contabilidad": {"name": _("Contabilidad"), "img": var.IMG_CALC, 
        "color": "#7D3C98"},
    }

    items = {
        1001: ("ventas", VentasPorFecha, "VENTAS POR FECHA"),
        1002: ("ventas", VentasPorRangoDeFechas, "VENTAS POR RANGO DE FECHAS"),
        2001: ("inventario", BalanceDeInventario, "BALANCE DE INVENTARIO"),
        3001: ("contabilidad", BalanceDeClientes, "BALANCE DE CLIENTES"),
        3002: ("contabilidad", PagosDeClientesDetallado, "PAGOS DE CLIENTES"),
        
    }
    
    def __getitem__(self, id):
        return self.build_item(id)

    @classmethod
    def get(self, id):
        return self.build_item(id)
    
    @classmethod
    def get_from_group(self, group_name):
        out = {}
        group_name = group_name.lower()
        for id in self.items:
            if self.items[id][0] == group_name:
                out[id] = self.build_item(id)

    @classmethod
    def all(self):
        return {int(id): self.build_item(id) for id in self.items}

    @classmethod
    def build_item(self, id):
        item = self.items[int(id)]
        group = self.groups[item[0]]
        group["key"] = item[0]
        return {
            "id": int(id),
            "group": group,
            "report_classs": item[1],
            "name": _(item[2]),
            "description": _(item[1].__doc__.strip()),
            "url": reverse_lazy("reporte-generic-detail", kwargs={"reportid": int(id)})
        }


    



