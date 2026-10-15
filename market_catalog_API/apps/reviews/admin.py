from django.contrib import admin

from apps.reviews.models import Review, Wishlist


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "rating", "is_approved", "created_at")
    list_filter = ("is_approved", "rating", "created_at")
    search_fields = ("user__email", "product__title", "product__sku", "comment")
    list_select_related = ("user", "product")
    readonly_fields = ("created_at",)
    actions = ("approve_reviews", "hide_reviews")

    @admin.action(description="Approve selected reviews", permissions=["change"])
    def approve_reviews(self, request, queryset):
        queryset.update(is_approved=True)

    @admin.action(description="Hide selected reviews", permissions=["change"])
    def hide_reviews(self, request, queryset):
        queryset.update(is_approved=False)


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "added_at")
    list_filter = ("added_at",)
    search_fields = ("user__email", "product__title", "product__sku")
    list_select_related = ("user", "product")
    readonly_fields = ("added_at",)
