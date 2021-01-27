from django import forms
import warnings
from django.core.exceptions import FieldError
from django.utils.html import format_html
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from unoletutils.libs import icons


class ModelForm(forms.ModelForm):
    """
    Clase ModelForm base para los formularios de modelos que 
    requieren la 'company' instancia.
    """

    def __init__(self, *args, **kwargs):
        try:
            self.company = kwargs.pop("company")
        except (KeyError):
            warnings.warn("El formulario '{self}' no tiene la instancia 'company'.")
            self.company = None

        super().__init__(*args, **kwargs)

        self.set_company_to_instance(self.instance, self.company)
        self.set_company_to_company_field(self.fields.get("company"), self.company)

        # Los campos que tenga un 'queryset' atributo, como ModelChoiceField...
        # dicho queryset será filtrado por la empresa actual.
        for key in self.fields:
            if key == "company":
                continue
            field = self.fields[key]
            if hasattr(field, "queryset"):
                qs = field.queryset
                try:
                    qs = qs.filter(**{qs.model.COMPANY_FIELD_NAME: self.company})
                except (FieldError) as e:
                    raise FieldError(key, "Debe establecer la variable "
                        "COMPANY_FIELD_NAME en el modelo, apuntando a la campo "
                        "que contiene la 'compnay' instancia.", e)
                self.fields[key].queryset = qs

    def __getitem__(self, name):
        """Return a BoundField with the given name."""
        try:
            field = self.fields[name]
        except (KeyError):
            return super().__getitem__(name)

        # En negrita el label del campo requerido.
        if field.required:
            field.widget.attrs.update({"placeholder": field.label})
            field.label = format_html("<b>{}</b>", field.label)

        # Alineamos los campos numéricos a la derecha.
        if isinstance(field.widget, forms.NumberInput):
            field.widget.attrs.update({"class": "text-end"})

        # Establecemos el widget ideal para campos de fechas.
        if isinstance(field, forms.DateField):
            field.widget = forms.DateInput(attrs={"type": "date"})
        
        return super().__getitem__(name)

    def set_company_to_instance(self, instance, company):
        """Establece el objeto 'company' a la instancia."""
        if instance and company:
            if not instance.pk:
                if hasattr(instance, "company"):
                    instance.company = company

    def set_company_to_company_field(self, field, company, disabled=True):
        """
        Establece el objeto 'company' al campo donde se establece. Este 
        campo deberá ser un ChoiceModelField.
        """
        if field and company:
            field.queryset = company._meta.model.objects.filter(pk=company.pk)
            field.initial = company
            field.disabled = bool(disabled)
            field.label = ""
            field.widget.attrs.update({"style": "display: none"})


class SearchForm(forms.Form):
    """Formulario para búsqueda."""

    tags__icontains = forms.CharField(label="", max_length=50, strip=True, 
    required=False, widget=forms.TextInput(
        attrs={"type": "search", "placeholder": _l("Buscar...")}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)