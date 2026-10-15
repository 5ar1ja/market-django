from django.contrib.admin import register, ModelAdmin
from django.utils.safestring import mark_safe
from django.core.handlers.wsgi import WSGIRequest

from apps.auths.models import CustomUser

@register(CustomUser)
class CustomUserAdmin(ModelAdmin):
    """
    Admin panel for CustomUser model.
    """

    list_display = (
        "id",
        "email",
        "first_name",
        "last_name",
        "phone_number",
        "is_active",
    )

    list_filter = (
        "is_active",
        "is_staff",
    )

    readonly_fields = (
        "id",
        "phone_number",
        "is_active",
        "is_staff",
        "created_at",
        "updated_at",
    )

    