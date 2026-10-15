from django.conf import settings
from django.db.models import (
    Model,
    ForeignKey,
    PROTECT,
    CharField, TextField, DecimalField, BooleanField, DateTimeField, CASCADE, SET_NULL, PositiveIntegerField,
)

from apps.products.models import Product


class Order(Model):
    STATUS_MAX_LEN = 20
    NAME_MAX_LEN = 50
    EMAIL_MAX_LEN = 75
    PHONE_MAX_LEN = 20
    PRICE_MAX_DIGITS = 12
    PRICE_DECIMAL_PLACES = 2

    STATUS_CREATED = 'created'
    STATUS_PAID = 'paid'
    STATUS_IN_DELIVERY = 'in_delivery'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELED = 'canceled'
    STATUS_CANCELLED = 'status_cancelled'

    STATUS_CHOICES = (
        (STATUS_CREATED, 'Created'),
        (STATUS_PAID, 'Paid'),
        (STATUS_IN_DELIVERY, 'In delivery'),
        (STATUS_CANCELED, 'Canceled'),
        (STATUS_CANCELLED, 'Cancelled'),
    )
    #ПОКУПАЕТЛЬ
    user = ForeignKey(
        to=settings.AUTH_USER_MODEL,
        on_delete=PROTECT,
        related_name="orders",
    )
    status = CharField(
        max_length=STATUS_MAX_LEN,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
    )

    #КОНТАКТНЫЕ ДАННЫЕ НА МОМЕНТ ЗАКАЗА
    first_name = CharField(max_length=NAME_MAX_LEN)
    last_name = CharField(max_length=NAME_MAX_LEN)
    email = CharField(max_length=EMAIL_MAX_LEN)
    phone = CharField(max_length=PHONE_MAX_LEN)
    delivery_address = TextField()

    total_amount = DecimalField(max_digits=PRICE_MAX_DIGITS, decimal_places=PRICE_DECIMAL_PLACES,default=0)
    payment_status= BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

class Meta:
        ordering = ("-created_at",)

        def __str__(self) -> str:
            return f"Order #{self.id}({self.get_status_display()})"

        def recalculate_total(self) -> None:
            total= 0
            for item in self.items.all():
                total += item.get_cost()
            self.total_amount = total
            self.save(update_fields=["total_amount", "updated_at"])

class OrderItem(Model):
        TITLE_MAX_LEN = 200
        SKU_MAX_LEN=50
        PRICE_MAX_DIGITS = 10
        PRICE_DECIMAL_PLACES = 2

        order = ForeignKey(
            to=Order,
            related_name="items",
            on_delete=CASCADE,
        )
        product = ForeignKey(
            to=Product,
            on_delete=SET_NULL,
            null=True,
            blank=True,
        )

        #снимать товар на моменте покупки
        product_title = CharField(max_length=TITLE_MAX_LEN, blank=True)
        product_sku = CharField(max_length=SKU_MAX_LEN, blank=True)
        price = DecimalField(
            max_digits=PRICE_MAX_DIGITS,
            decimal_places=PRICE_DECIMAL_PLACES,
            null=True,
            blank=True,
        )
        quantity = PositiveIntegerField(default=1)

        def __str__(self) -> str:
            return f"{self.product_title} ({self.quantity}x)"
        def save(self, *args, **kwargs) -> None:
            #если пустой снимок берем данные с товара
            if self.product is not None:
                if not self.product_title:
                    self.product_title = self.product.title
                if not self.product_sku:
                    self.product_sku = self.product.sku
                if self.price is None:
                    self.price = self.product.price
            super().save(*args, **kwargs)

        def get_cost(self):
            if self.price is None:
                return 0
            return self.price * self.quantity