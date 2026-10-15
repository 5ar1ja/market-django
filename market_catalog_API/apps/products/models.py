from django.db.models import (
    CASCADE,
    PROTECT,
    SET_NULL,
    BooleanField,
    CharField,
    DateTimeField,
    DecimalField,
    ForeignKey,
    ImageField,
    Model,
    PositiveIntegerField,
    SlugField,
    TextField,
)

class Category(Model):
    TITLE_MAX_LEN = 150
    SLUG_MAX_LEN = 150

    title = CharField(max_length=TITLE_MAX_LEN)
    slug = SlugField(max_length=SLUG_MAX_LEN, unique=True)
    parent = ForeignKey(
            to="self",
            on_delete=CASCADE,
            null=True,
            blank=True,
        )
    is_active = BooleanField(default=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self)-> str:
        return self.title

class Brand(Model):
    NAME_MAX_LEN = 150
    SLUG_MAX_LEN = 150

    name = CharField(max_length=NAME_MAX_LEN)
    slug = SlugField(max_length=SLUG_MAX_LEN, unique=True)
    logo = ImageField(upload_to="brands/", null=True, blank=True)
    

    def __str__(self)-> str:
        return self.name


class Product(Model):
    TITLE_MAX_LEN = 200
    SLUG_MAX_LEN = 200
    SKU_MAX_LEN=50
    PRICE_MAX_DIGITS = 10
    PRICE_DECIMAL_PLACES = 2

    category = ForeignKey(
        to=Category,
        on_delete=PROTECT,
    )
    brand = ForeignKey(
        to=Brand,
        on_delete=SET_NULL,
        null=True,
        blank=True,
    )
    title = CharField(max_length=TITLE_MAX_LEN)
    slug = SlugField(max_length=SLUG_MAX_LEN, unique=True)
    sku = CharField(max_length=SKU_MAX_LEN, unique=True)
    description = TextField()
    price = DecimalField(
        max_digits=PRICE_MAX_DIGITS,
        decimal_places=PRICE_DECIMAL_PLACES,
    )
    old_price = DecimalField(
        max_digits=PRICE_MAX_DIGITS,
    decimal_places=PRICE_DECIMAL_PLACES,
    null=True,
    blank=True,
)
    stock = PositiveIntegerField(default=0)
    is_available = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    def __str__(self)-> str:
        return self.title


class ProductImage(Model):
    product = ForeignKey(
        to=Product,
        related_name="images",
        on_delete=CASCADE,
    )
    image = ImageField(upload_to="products/")
    is_main = BooleanField(default=False)
    order = PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self)-> str:
        return f"{self.product.title}:image {self.order}"


class ProductAttribute(Model):
    NAME_MAX_LEN = 100

    name = CharField(max_length=NAME_MAX_LEN)

    def __str__(self)-> str:
        return self.name


class ProductAttributeValue(Model):
    VALUE_MAX_LEN = 255

    product = ForeignKey(
        to=Product,
        related_name="attributes",
        on_delete=CASCADE,
    )
    attribute = ForeignKey(
        to=ProductAttribute,
        on_delete=CASCADE,
    )
    value = CharField(max_length=VALUE_MAX_LEN)

    def __str__(self)-> str:
        return f"{self.attribute.name}: {self.value}"