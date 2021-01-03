from django import forms 

from base.forms import ModelForm
from company.models import Company
from .models import (Item, ItemFamily, ItemGroup, Movement)


class ItemForm(ModelForm):
    """Formulario para artículos."""

    class Meta:
        model = Item
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #if not self.instance.pk:
        #    self.instance.company = self.company

        #self.fields["company"].queryset = Company.objects.filter(pk=self.company.pk)
        #self.fields["company"].initial = self.company
        #self.fields["company"].disabled = True

        