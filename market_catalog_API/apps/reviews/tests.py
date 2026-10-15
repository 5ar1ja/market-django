from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.forms import modelform_factory
from django.test import TestCase
from django.utils import timezone

from apps.products.models import Category, Product
from apps.reviews.models import Review, Wishlist


class MarketplaceFixture(TestCase):
    @classmethod
    def setUpTestData(cls):
        User = get_user_model()
        cls.alice = User.objects.create_user("alice@example.test", None)
        cls.bob = User.objects.create_user("bob@example.test", None)
        cls.category = Category.objects.create(title="Books", slug="books")
        cls.book = Product.objects.create(
            category=cls.category, title="Django book", slug="django-book",
            sku="BOOK-1", description="A test product", price="25.00",
        )
        cls.other_book = Product.objects.create(
            category=cls.category, title="Python book", slug="python-book",
            sku="BOOK-2", description="Another test product", price="20.00",
        )

    def make_review(self, **overrides):
        return Review.objects.create(**{
            "user": self.alice, "product": self.book,
            "rating": 4, "comment": "Useful examples.", **overrides,
        })


class ReviewModelTests(MarketplaceFixture):
    def test_valid_review_has_defaults_and_aware_timestamp(self):
        review = self.make_review()
        review.full_clean()
        self.assertTrue(review.is_approved)
        self.assertTrue(timezone.is_aware(review.created_at))
        self.assertEqual(review.user, self.alice)
        self.assertEqual(review.product, self.book)

    def test_rating_boundaries_are_valid(self):
        for rating in (1, 5):
            with self.subTest(rating=rating):
                Review(user=self.alice, product=self.book, rating=rating, comment="Valid.").full_clean()

    def test_invalid_ratings_fail_model_validation(self):
        for rating in (0, 6):
            with self.subTest(rating=rating), self.assertRaises(ValidationError) as error:
                Review(user=self.alice, product=self.book, rating=rating, comment="Invalid.").full_clean()
            self.assertIn("rating", error.exception.message_dict)

    def test_database_rejects_out_of_range_ratings_without_full_clean(self):
        for rating in (0, 6):
            with self.subTest(rating=rating), self.assertRaises(IntegrityError), transaction.atomic():
                self.make_review(rating=rating)

    def test_database_check_also_protects_queryset_updates(self):
        review = self.make_review()
        with self.assertRaises(IntegrityError), transaction.atomic():
            Review.objects.filter(pk=review.pk).update(rating=9)
        review.refresh_from_db()
        self.assertEqual(review.rating, 4)

    def test_same_user_cannot_review_same_product_twice(self):
        self.make_review()
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.make_review(comment="Duplicate.")

    def test_duplicate_review_is_reported_by_full_clean(self):
        self.make_review()
        duplicate = Review(user=self.alice, product=self.book, rating=3, comment="Duplicate.")
        with self.assertRaises(ValidationError):
            duplicate.full_clean()

    def test_distinct_user_product_pairs_are_allowed(self):
        self.make_review()
        self.make_review(user=self.bob)
        self.make_review(product=self.other_book)
        self.assertEqual(Review.objects.count(), 3)

    def test_comment_is_required_during_model_validation(self):
        review = Review(user=self.alice, product=self.book, rating=4, comment="")
        with self.assertRaises(ValidationError) as error:
            review.full_clean()
        self.assertIn("comment", error.exception.message_dict)

    def test_reverse_relationships_use_existing_user_and_product(self):
        review = self.make_review()
        self.assertEqual(list(self.book.reviews.all()), [review])
        self.assertEqual(list(self.alice.review_set.all()), [review])
        self.assertEqual(Review._meta.get_field("user").remote_field.model, get_user_model())

    def test_hidden_reviews_require_an_explicit_approved_filter(self):
        visible = self.make_review()
        hidden = self.make_review(user=self.bob, is_approved=False)
        self.assertEqual(list(Review.objects.filter(is_approved=True)), [visible])
        self.assertIn(hidden, Review.objects.all())

    def test_deleting_user_cascades_reviews_without_deleting_product(self):
        self.make_review()
        self.alice.delete()
        self.assertFalse(Review.objects.exists())
        self.assertTrue(Product.objects.filter(pk=self.book.pk).exists())

    def test_deleting_product_cascades_reviews_without_deleting_user(self):
        self.make_review()
        self.book.delete()
        self.assertFalse(Review.objects.exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.alice.pk).exists())

    def test_ordering_is_stable_when_timestamps_match(self):
        first = self.make_review()
        second = self.make_review(user=self.bob)
        Review.objects.update(created_at=timezone.now())
        self.assertEqual(list(Review.objects.values_list("pk", flat=True)), [second.pk, first.pk])

    def test_string_representation_identifies_review(self):
        self.assertEqual(str(self.make_review()), "alice@example.test: Django book (4/5)")

    def test_model_form_validates_rating_before_saving(self):
        ReviewForm = modelform_factory(Review, fields=("user", "product", "rating", "comment"))
        data = {"user": self.alice.pk, "product": self.book.pk, "rating": 6, "comment": "Test."}
        invalid = ReviewForm(data)
        self.assertFalse(invalid.is_valid())
        self.assertIn("rating", invalid.errors)
        valid = ReviewForm({**data, "rating": 5})
        self.assertTrue(valid.is_valid(), valid.errors)
        self.assertEqual(valid.save().rating, 5)


class WishlistModelTests(MarketplaceFixture):
    def test_wishlist_entry_has_timestamp_and_reverse_relationships(self):
        entry = Wishlist.objects.create(user=self.alice, product=self.book)
        entry.full_clean()
        self.assertTrue(timezone.is_aware(entry.added_at))
        self.assertEqual(list(self.alice.wishlist.all()), [entry])
        self.assertEqual(list(self.book.wishlist_set.all()), [entry])

    def test_duplicate_wishlist_entry_is_rejected_by_database(self):
        Wishlist.objects.create(user=self.alice, product=self.book)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Wishlist.objects.create(user=self.alice, product=self.book)

    def test_duplicate_wishlist_entry_is_reported_by_full_clean(self):
        Wishlist.objects.create(user=self.alice, product=self.book)
        with self.assertRaises(ValidationError):
            Wishlist(user=self.alice, product=self.book).full_clean()

    def test_distinct_pairs_are_allowed(self):
        for user, product in [(self.alice, self.book), (self.bob, self.book), (self.alice, self.other_book)]:
            Wishlist.objects.create(user=user, product=product)
        self.assertEqual(Wishlist.objects.count(), 3)

    def test_get_or_create_makes_repeated_save_idempotent(self):
        first, created_first = Wishlist.objects.get_or_create(user=self.alice, product=self.book)
        second, created_second = Wishlist.objects.get_or_create(user=self.alice, product=self.book)
        self.assertTrue(created_first)
        self.assertFalse(created_second)
        self.assertEqual(first.pk, second.pk)

    def test_user_deletion_cascades_wishlist(self):
        Wishlist.objects.create(user=self.alice, product=self.book)
        self.alice.delete()
        self.assertFalse(Wishlist.objects.exists())
        self.assertTrue(Product.objects.filter(pk=self.book.pk).exists())

    def test_product_deletion_cascades_wishlist(self):
        Wishlist.objects.create(user=self.alice, product=self.book)
        self.book.delete()
        self.assertFalse(Wishlist.objects.exists())
        self.assertTrue(get_user_model().objects.filter(pk=self.alice.pk).exists())

    def test_ordering_is_stable_when_timestamps_match(self):
        first = Wishlist.objects.create(user=self.alice, product=self.book)
        second = Wishlist.objects.create(user=self.bob, product=self.book)
        Wishlist.objects.update(added_at=timezone.now())
        self.assertEqual(list(Wishlist.objects.values_list("pk", flat=True)), [second.pk, first.pk])

    def test_string_representation_identifies_entry(self):
        entry = Wishlist(user=self.alice, product=self.book)
        self.assertEqual(str(entry), "alice@example.test: Django book")
