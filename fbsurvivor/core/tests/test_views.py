from django.test import TestCase
from django.urls import reverse

from fbsurvivor.core.models import Season


class HomePageTest(TestCase):
    def setUp(self) -> None:
        Season.objects.create(year=2020, is_locked=False, is_current=True)

    def test_home_url_exists(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_home_reverse_exists(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
