from django.test import TestCase

from projects.models import Project
from users.models import User


class UserListFilterTests(TestCase):
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
        self.project = Project.objects.create(name="P1", description="", owner=self.owner, status="open")
        self.project.participants.add(self.user)

    def test_filter_owners_of_participating_projects(self):
        self.client.login(username=self.user.email, password="pass12345")
        resp = self.client.get("/users/list/?filter=owners-of-participating-projects")
        self.assertEqual(resp.status_code, 200)
        # owner should be included
        self.assertContains(resp, self.owner.name)

