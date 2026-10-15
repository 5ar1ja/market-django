from django.contrib.admin import ModelAdmin, TabularInline, register

from apps.products.models import (
    Brand, 
    Category, 
    Product,
    ProductAttribute,
    ProductAttributeValue,
    ProductImage,
)

@register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ("id", "title", "parent", "is_active")
    search_fields = ("title", "slug")
    list_filter = ("is_active", "parent")
    prepopulated_fields = {"slug": ("title",)}


@register(Brand)
class BrandAdmin(ModelAdmin):
    list_display = ("id", "name", "slug")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}

class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1
    fields = ("image", "is_main", "order")

class ProductAttributeValueInline(TabularInline):
    model = ProductAttributeValue
    extra = 1
    fields = ("attribute", "value")


@register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "id",
        "title",
        "sku",
        "brand",
        "category",
        "price",
        "stock",
        "is_available",
    )
    search_fields = ("title", "sku", "slug")
    list_filter = ("brand", "category", "is_available")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25
    inlines = (ProductImageInline, ProductAttributeValueInline)

    fieldsets = (
        (
            "General",
            {
                "fields": (
                    "title",
                    "slug",
                    "sku",
                    "description",
                    "category",
                    "brand",
                )}
        ),
        (
            "Price and stock",
            {
                "fields": (
                    "price",
                    "old_price",
                    "stock",
                    "is_available",
                )
            }
        ),
        (
            "Dates",
            {
                "fields":("created_at", "updated_at"),
            }
        )
    )


@register(ProductImage)
class ProductImageAdmin(ModelAdmin):
    list_display = ("id", "product", "is_main", "order")
    search_fields = ("product_title", "product_sku")
    list_filter = ("is_main",)


@register(ProductAttribute)
class ProductAttributeAdmin(ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@register(ProductAttributeValue)
class ProductAttributeValueAdmin(ModelAdmin):
    list_display = ("id", "product", "attribute", "value")
    search_fields = ("product__title", "attribute__name", "value")
    list_filter = ("attribute",)
        