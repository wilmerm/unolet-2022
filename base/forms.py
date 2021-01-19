from django import forms
from django.utils.html import format_html
from django.utils.translation import gettext as _


class ModelForm(forms.ModelForm):
    """
    Clase ModelForm base para los formularios de modelos que 
    requieren la 'company' instancia.
    """

    def __init__(self, *args, **kwargs):
        try:
            self.company = kwargs.pop("company")
        except (KeyError):
            self.company = None

        super().__init__(*args, **kwargs)

        self.set_company_to_instance(self.instance, self.company)
        self.set_company_to_company_field(self.fields.get("company"), self.company)

    def __getitem__(self, name):
        """Return a BoundField with the given name."""
        try:
            field = self.fields[name]
        except (KeyError):
            return super().__getitem__(name)

        # Agregamos un asterisco si el campo es requerido.
        if field.required:
            field.label = format_html(
                '{} <span title="{}" class="text-danger">*</span>', 
                field.label, _("Requerido."))

        # Alineamos los campos numéricos a la derecha.
        if isinstance(field.widget, forms.NumberInput):
            field.widget.attrs.update({"class": "text-end"})    
        
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
