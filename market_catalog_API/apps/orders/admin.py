from django.contrib.admin import ModelAdmin, TabularInline, register

from apps.orders.models import Order, OrderItem

class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 1
    fields = ( "product", "product_title", "product_sku", "price", "quantity")

@register(Order)
class OrderAdmin(ModelAdmin):
    list_display = ("id", "user", "status", "created_at",
                    "first_name", "last_name", "phone", "total_amount",
                    "payment_status")
    search_fields = ("id", "email", "phone", "first_name", "last_name")
    list_filter = ("status", "payment_status", "created_at")
    readonly_fields = ("created_at", "updated_at", "total_amount")
    list_per_page = 25
    inlines = (OrderItemInline,)
    fieldsets = (
    (
        "General",
        {
            "fields":(
                "user","status","payment_status","total_amount",
            )
        }
    ),(
        "Contacts",
        {
            "fields": ("first_name", "last_name", "email", "phone", "delivery_address")
        }
    ),
    (
        "Dates",
        {
            "fields":("created_at", "updated_at"),
        }
    )
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.recalculate_total()

@register(OrderItem)
class OrderItemAdmin(ModelAdmin):
    list_display = ("id", "order", "product", "product_title", "product_sku", "price", "quantity")
    search_fields = ("product_title", "product_sku")