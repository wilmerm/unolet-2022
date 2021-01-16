from django.urls import path 

from document import views
from document.models import DocumentType


urlpatterns = [
    path("", views.Index.as_view(), name="document-index"),

    # Json views.

    path("json/document/<int:document>/movement/list/", 
    views.document_movements_jsonview, 
    name="document-document-movement-list-json"),

    # django-autocomplete-light.

    path("json/documenttype/<str:generictype>/list/", 
    views.DocumentTypeAutocompleteView.as_view(),
    name="document-autocomplete-documenttype"),
]


# Creamos los path de forma dinámica para cada tipo genérico de documento.

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
    