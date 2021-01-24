


from base.forms import ModelForm
from document.models import DocumentType, Document
from finance.models import (Currency, Transaction)


class TransactionForm(ModelForm):
    """
    Formulario para la creación y modificación de transacciones.

    Todas las transacciones se aplican a un documento en particular. Según la
    configuración del tipo de dicho documento, la transacción se comportará 
    como crédito o débito.
    """
    
    class Meta:
        model = Transaction
        exclude = ["document"]

    def __init__(self, *args, **kwargs):
        self.document = kwargs.pop("document")
        super().__init__(*args, **kwargs)

        self.instance.document = self.document

        


    