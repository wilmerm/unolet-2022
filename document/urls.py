from django.urls import path 
from . import views


urlpatterns = [
    path("document/<int:pk>/update/", views.DocumentUpdateView.as_view(), name="document-document-update"),
]