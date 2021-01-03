from django import forms
from django.utils.translation import gettext as _
from django.utils.translation import gettext_lazy as _l

from .models import Company


class CompanyForm(forms.ModelForm):
    """Formulario para las empresas."""

    class Meta:
        model = Company
        fields = "__all__"

    def clean(self):
        admin_users = self.cleaned_data.get("admin_users")
        if not admin_users:
            raise forms.ValidationError({"admin_users": 
                _("Debe existir al menos un administrador.")})