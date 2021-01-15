from django.contrib import admin
from django.utils.html import format_html, html_safe

from module.models import Module



@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("get_icon", "get_name", "description", "url_name", "get_parent")
    list_display_links = ("get_icon", "get_name")

    def get_icon(self, obj):
        return format_html(obj.get_svg()["svg"])

    def get_name(self, obj):
        return format_html('<div style="padding: 1px; background-color: {}; color: {}">{}</div>',
            obj.css_bgcolor, obj.css_textcolor, obj)

    def get_parent(self, obj):
        if obj.parent:
            return self.get_name(obj.parent)
        return ""