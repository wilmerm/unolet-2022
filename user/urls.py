from django.urls import path, include
from . import views 



urlpatterns = [
    # on company.
    path("<int:company>/", views.IndexView.as_view(), name="user-index"),
    path("user/list/", views.UserListView.as_view(), name="user-user-list"),

    path("accounts/", include("django.contrib.auth.urls")),
]