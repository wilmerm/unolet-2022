from django.urls import path 
from . import views


urlpatterns = [
    path("document/create/", views.DocumentCreateView.as_view(), name="document-document-create"),
    path("document/<int:pk>/update/", views.DocumentUpdateView.as_view(), name="document-document-update"),
]