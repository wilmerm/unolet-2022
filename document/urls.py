from django.urls import path 

from document import views
from document.models import DocumentType


urlpatterns = [
    path("", views.Index.as_view(), name="document-index"),

    path("document/<str:generictype>/create/", 
    views.DocumentCreateView.as_view(), name="document-document-create"),

    path("document/<str:generictype>/list/", 
    views.DocumentListView.as_view(), name="document-document-list"),

    #path("document/<str:generictype>/<int:pk>/", 
    #views.DocumentDetailView.as_view(), name="document-document-detail"),

    path("document/<str:generictype>/<int:pk>/update/", 
    views.DocumentUpdateView.as_view(), name="document-document-update"),

    path("document/<str:generictype>/<int:pk>/delete/", 
    views.DocumentDeleteView.as_view(), name="document-document-delete"),

    # Json views.

    path("api/document/<int:document>/", 
    views.document_detail_jsonview, 
    name="api-document-document-detail"),

    path("api/document/<int:document>/documentnote/create/", 
    views.document_note_create_jsonview, 
    name="api-document-document-documentnote-create"),

    path("api/document/<int:document>/documentnote/list/", 
    views.document_note_list_jsonview, 
    name="api-document-document-documentnote-list"),

    path("api/document/<int:document>/documentnote/delete/", 
    views.document_note_delete_jsonview, 
    name="api-document-document-documentnote-delete"),

    # django-autocomplete-light.

    path("autocomplete/documenttype/<str:generictype>/list/", 
    views.DocumentTypeAutocompleteView.as_view(),
    name="document-autocomplete-documenttype"),
]


# Creamos los path de forma dinámica para cada tipo genérico de documento, 
# para ser utilizado cuando se conoce el tipo genérico por anticipado.
# Útil por ejemplo para ser usado en la definición de módulos.

for generictype, verbose_name in DocumentType.GENERIC_TYPE_CHOICES:
    try:
        pattern_create = path(f"document/{generictype}/create/", 
            views.DocumentCreateView.as_view(generictype=generictype, 
            template_name=f"document/document/{generictype}_form.html"), 
            name=f"document-document-{generictype}-create")
    except (AttributeError):
        pass
    else:
        urlpatterns.append(pattern_create)
    
    try:
        pattern_list = path(f"document/{generictype}/list/", 
            views.DocumentListView.as_view(generictype=generictype), 
            name=f"document-document-{generictype}-list")
    except (AttributeError):
        pass
    else:
        urlpatterns.append(pattern_list)

    try:
        pattern_detail = path(f"document/{generictype}/<int:pk>/detail/", 
            views.DocumentDetailView.as_view(generictype=generictype), 
            name=f"document-document-{generictype}-detail")
    except (AttributeError):
        pass
    else:
        urlpatterns.append(pattern_detail)

    try:
        pattern_update = path(f"document/{generictype}/<int:pk>/update/", 
            views.DocumentUpdateView.as_view(generictype=generictype, 
            template_name=f"document/document/{generictype}_form.html"), 
            name=f"document-document-{generictype}-update")
    except (AttributeError):
        pass
    else:
        urlpatterns.append(pattern_update)

    try:
        pattern_delete = path(f"document/{generictype}/<int:pk>/delete/", 
            views.DocumentDeleteView.as_view(generictype=generictype), 
            name=f"document-document-{generictype}-delete")
    except (AttributeError):
        pass
    else:
        urlpatterns.append(pattern_delete)
    