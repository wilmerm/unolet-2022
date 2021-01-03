from django import forms 


class ModelForm(forms.ModelForm):
    """
    Clase ModelForm base para los formularios de modelos que 
    requieren la 'company' variable.
    """

    def __init__(self, *args, **kwargs):
        try:
            self.company = kwargs.pop("company")
        except (KeyError):
            self.company = None

        super().__init__(*args, **kwargs)

        self.set_company_to_instance(self.instance, self.company)
        self.set_company_to_company_field(self.fields.get("company"), self.company)

    def set_company_to_instance(self, instance, company):
        """Establece el objeto 'company' a la instancia."""
        if instance and company:
            if not instance.pk:
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
