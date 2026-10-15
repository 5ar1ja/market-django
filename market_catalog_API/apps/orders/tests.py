from decimal import Decimal

from django.db.models import ProtectedError
from django.test import TestCase

from apps.auths.models import CustomUser
from apps.orders.models import Order, OrderItem
from apps.products.models import Category, Product


class OrderTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(email="buyer@test.kz", password="12345678")
        category = Category.objects.create(title="Books", slug="books")
        self.product = Product.objects.create(category=category, title="Django book", slug="django-book", sku="BOOK-1", description="A test product", price="25.00")
        self.order = Order.objects.create(
            user=self.user,
            first_name="John",
            last_name="Ivanov",
            email="john@gmail.com",
            phone="+7777777777",
            delivery_address="Moscow, Lenina street, 123",
        )
    def test_default_status(self):
        self.assertEqual(self.order.status, Order.STATUS_CREATED)
        self.assertEqual(self.order.payment_status)

    def test_item_snapshot(self):
        item = OrderItem.objects.create(order=self.order, product=self.product, quantity=2, price=Decimal("10.00"))
        self.assertEqual(item.product_title, "Django book")
        self.assertEqual(item.product_sku, "BOOK-1")
        self.assertEqual(item.price, Decimal("10.00"))
