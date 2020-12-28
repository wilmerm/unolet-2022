

from django import forms

from fuente.report.fields import (IntegerField, DecimalField, FloatField,
    TextField)


class FormSearch(forms.Form):
    """
    Formulario genérico para filtros de búsquedas en los reportes.
    """

    def __init__(self, *args, **kwargs):
        try:
            self.rfields = kwargs.pop("rfields")
        except (KeyError):
            self.rfields = []
        super().__init__(*args, **kwargs)

        for name, field in self.rfields:
            #self.fields[rfield.name] = self.CreateFieldFromReportField(rfield)
            self.fields[name] = field

    def __call__(self, *args, **kwargs):
        kwargs["rfields"] = self.rfields
        return self.__class__(*args, **kwargs)

    def CreateFieldFromReportField(self, report_field):
        """
        Crea la instancia de Django form field correspondiente según la field de
        reporte indicada.

        Parameters:
            report_field (fuente.report.fields.FieldBase)

        Returns:
            report_field.form_field_class()

        """
        field_class = report_field.form_field_class
        field = field_class(label=report_field.verbose_name)
        if hasattr(report_field, "form_field_widget_class"):
            field.widget = report_field.form_field_widget_class(attrs=report_field.form_field_widget_attrs)
        return field
