from django.contrib import admin

from apps.cart.models import Cart, CartItem

class CartItemInline(admin.TabularInline):
    model=CartItem
    extra=1

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "get_total_items",
        "get_total_price",
        "updated_at",
    )
    search_fields=("user__email","session_key")
    inlines=(CartItemInline,)

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display=("id","cart", "product","quantity","created_at")
    search_fields=("product__title",)
