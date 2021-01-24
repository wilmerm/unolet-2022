
from base.forms import ModelForm
from person.models import Person


class PersonForm(ModelForm):
    """Formulario de creación y modificación de personas."""

    class Meta:
        model = Person
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        

        