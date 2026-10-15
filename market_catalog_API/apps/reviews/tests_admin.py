from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.test import RequestFactory
from django.urls import reverse

from apps.reviews.models import Review, Wishlist
from apps.reviews.tests import MarketplaceFixture


class ReviewAdminTests(MarketplaceFixture):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        User = get_user_model()
        cls.admin_user = User.objects.create_superuser("admin@example.test", "Study-reviews-7!Long")
        cls.staff = User.objects.create_user("staff@example.test", None, is_staff=True)
        cls.review = Review.objects.create(user=cls.alice, product=cls.book, rating=4, comment="Useful.")
        cls.wish = Wishlist.objects.create(user=cls.alice, product=cls.book)

    def test_both_models_have_working_list_add_and_change_pages(self):
        self.client.force_login(self.admin_user)
        for obj in (self.review, self.wish):
            name = obj._meta.model_name
            urls = [reverse(f"admin:reviews_{name}_changelist"),
                    reverse(f"admin:reviews_{name}_add"),
                    reverse(f"admin:reviews_{name}_change", args=[obj.pk])]
            for url in urls:
                with self.subTest(url=url):
                    self.assertEqual(self.client.get(url).status_code, 200)

    def test_related_search_works_for_both_models(self):
        self.client.force_login(self.admin_user)
        for obj in (self.review, self.wish):
            for query in ("alice@example.test", "Django book", "BOOK-1"):
                with self.subTest(model=obj._meta.model_name, query=query):
                    response = self.client.get(reverse(f"admin:reviews_{obj._meta.model_name}_changelist"), {"q": query})
                    self.assertEqual(list(response.context["cl"].queryset), [obj])

    def test_admin_validates_rating_and_can_create_valid_review(self):
        self.client.force_login(self.admin_user)
        url = reverse("admin:reviews_review_add")
        data = {"user": self.bob.pk, "product": self.book.pk, "rating": 6,
                "comment": "New review.", "is_approved": "on", "_save": "Save"}
        invalid = self.client.post(url, data)
        self.assertEqual(invalid.status_code, 200)
        self.assertIn("rating", invalid.context["adminform"].form.errors)
        response = self.client.post(url, {**data, "rating": 5})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.get(user=self.bob, product=self.book).rating, 5)

    def test_admin_rejects_duplicate_wishlist_entry(self):
        self.client.force_login(self.admin_user)
        response = self.client.post(reverse("admin:reviews_wishlist_add"), {
            "user": self.alice.pk, "product": self.book.pk, "_save": "Save",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["adminform"].form.non_field_errors())
        self.assertEqual(Wishlist.objects.count(), 1)

    def test_staff_with_change_permission_can_hide_and_approve_reviews(self):
        self.staff.user_permissions.add(Permission.objects.get(codename="change_review"))
        self.client.force_login(self.staff)
        url = reverse("admin:reviews_review_changelist")
        for action, expected in (("hide_reviews", False), ("approve_reviews", True)):
            with self.subTest(action=action):
                response = self.client.post(url, {
                    "action": action, "_selected_action": [self.review.pk], "index": "0",
                })
                self.assertEqual(response.status_code, 302)
                self.review.refresh_from_db()
                self.assertEqual(self.review.is_approved, expected)

    def test_view_only_staff_cannot_edit_or_run_moderation_actions(self):
        self.staff.user_permissions.add(Permission.objects.get(codename="view_review"))
        self.client.force_login(self.staff)
        change_url = reverse("admin:reviews_review_change", args=[self.review.pk])
        self.assertEqual(self.client.get(change_url).status_code, 200)
        self.assertEqual(self.client.post(change_url, {"is_approved": ""}).status_code, 403)
        request = RequestFactory().get("/admin/")
        request.user = get_user_model().objects.get(pk=self.staff.pk)
        actions = admin.site._registry[Review].get_actions(request)
        self.assertNotIn("approve_reviews", actions)
        self.assertNotIn("hide_reviews", actions)
        response = self.client.post(reverse("admin:reviews_review_changelist"), {
            "action": "hide_reviews", "_selected_action": [self.review.pk], "index": "0",
        })
        self.assertEqual(response.status_code, 200)
        self.review.refresh_from_db()
        self.assertTrue(self.review.is_approved)

    def test_anonymous_user_cannot_open_review_admin(self):
        response = self.client.get(reverse("admin:reviews_review_changelist"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("admin:login"), response.url)
