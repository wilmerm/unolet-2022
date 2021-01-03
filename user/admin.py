from django.contrib import admin
from .models import User



@admin.register(User)
class UserAdmin(admin.ModelAdmin):

    list_display = ["username", "get_full_name", "is_superuser", 
        "is_staff", "is_active", "last_login", "site"]
    
    search_fields = ["username", "first_name", "last_name", "email"]

    list_filter = ["is_superuser", "is_staff", "is_active", "site"]



