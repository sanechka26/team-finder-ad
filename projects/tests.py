from django.test import TestCase

from projects.models import Project
from users.models import User


class FavoriteToggleTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email="owner@example.com",
            password="pass12345",
            name="Owner",
            surname="One",
            phone="+79990000001",
        )
        self.user = User.objects.create_user(
            email="user@example.com",
            password="pass12345",
            name="User",
            surname="Two",
            phone="+79990000002",
        )
        self.project = Project.objects.create(name="P1", description="D", owner=self.owner, status="open")

    def test_toggle_favorite_requires_auth(self):
        resp = self.client.post(f"/projects/{self.project.id}/toggle-favorite/")
        self.assertIn(resp.status_code, (302, 403))

    def test_toggle_favorite_add_and_remove(self):
        self.client.login(username=self.user.email, password="pass12345")
        resp = self.client.post(f"/projects/{self.project.id}/toggle-favorite/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["status"], "ok")
        self.assertEqual(resp.json()["favorited"], True)
        self.assertTrue(self.user.favorites.filter(id=self.project.id).exists())

        resp2 = self.client.post(f"/projects/{self.project.id}/toggle-favorite/")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["favorited"], False)

    def test_favorites_page_requires_auth(self):
        resp = self.client.get("/projects/favorites/")
        self.assertEqual(resp.status_code, 302)

