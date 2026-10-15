from decimal import Decimal

from django.conf import settings
from django.db import models

class Cart(models.Model):
    user=models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
    )
    session_key=models.CharField(max_length=40,null=True, blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Cart #{self.id}"

    def get_total_price(self) -> Decimal:
        total = Decimal("0")
        for item in self.items.all():
            total += item.product.price * item.quantity
        return total

    def get_total_items(self) -> int:
        total=0
        for item in self.items.all():
            total += item.quantity
        return total

class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, related_name="items", on_delete=models.CASCADE

    )
    product = models.ForeignKey(
        "products.Product", on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["cart","product"], name ="cart_unique_cart_product"
            )
        ]
    def __str__(self) -> str:
        return f"{self.product} x {self.quantity}"
    
