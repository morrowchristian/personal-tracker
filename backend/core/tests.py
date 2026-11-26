"""Tests for the Task API (backend/core).

Covers the behaviour the app actually promises: authenticated task CRUD,
per-user isolation (a user can never see or touch another user's tasks),
the toggle endpoint, and rejection of unauthenticated requests.
"""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import Task

User = get_user_model()


class TaskApiTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username="alice", password="password123")
        self.bob = User.objects.create_user(username="bob", password="password123")
        self.alice_client = APIClient()
        self.alice_client.force_authenticate(user=self.alice)
        self.bob_client = APIClient()
        self.bob_client.force_authenticate(user=self.bob)
        self.anon_client = APIClient()

    def make_task(self, user, **kwargs):
        defaults = {"title": "Buy groceries"}
        defaults.update(kwargs)
        return Task.objects.create(owner=user, **defaults)

    def test_create_task_authenticated(self):
        """An authenticated user can create a task; it belongs to them."""
        response = self.alice_client.post(
            "/api/tasks/",
            {
                "title": "Finish report",
                "description": "Q3 summary",
                "due_date": "2026-12-01",
                "priority": "high",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Finish report")
        self.assertEqual(response.data["priority"], "high")
        self.assertEqual(response.data["due_date"], "2026-12-01")
        self.assertFalse(response.data["completed"])
        task = Task.objects.get(pk=response.data["id"])
        self.assertEqual(task.owner, self.alice)

    def test_create_task_requires_title(self):
        """Creating a task without a title is rejected."""
        response = self.alice_client.post(
            "/api/tasks/", {"description": "no title"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_returns_only_own_tasks(self):
        """A user lists only their own tasks, never another user's."""
        self.make_task(self.alice, title="Alice task 1")
        self.make_task(self.alice, title="Alice task 2")
        self.make_task(self.bob, title="Bob task")

        response = self.alice_client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        titles = [task["title"] for task in response.data]
        self.assertCountEqual(titles, ["Alice task 1", "Alice task 2"])

    def test_retrieve_other_users_task_returns_404(self):
        """Another user's task is invisible even by direct id."""
        task = self.make_task(self.alice, title="Alice secret")
        response = self.bob_client.get(f"/api/tasks/{task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_own_task(self):
        """An authenticated user can edit their own task."""
        task = self.make_task(self.alice, title="Old title", priority="low")
        response = self.alice_client.patch(
            f"/api/tasks/{task.pk}/",
            {"title": "New title", "priority": "high"},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.title, "New title")
        self.assertEqual(task.priority, "high")

    def test_update_other_users_task_returns_404(self):
        """Another user's task cannot be edited."""
        task = self.make_task(self.alice, title="Alice task")
        response = self.bob_client.patch(
            f"/api/tasks/{task.pk}/", {"title": "Hijacked"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        task.refresh_from_db()
        self.assertEqual(task.title, "Alice task")

    def test_toggle_task(self):
        """POST /toggle/ flips completed and flips it back."""
        task = self.make_task(self.alice, title="Toggle me")
        self.assertFalse(task.completed)

        response = self.alice_client.post(f"/api/tasks/{task.pk}/toggle/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["completed"])

        response = self.alice_client.post(f"/api/tasks/{task.pk}/toggle/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data["completed"])

    def test_toggle_other_users_task_returns_404(self):
        """Another user's task cannot be toggled."""
        task = self.make_task(self.alice, title="Alice task")
        response = self.bob_client.post(f"/api/tasks/{task.pk}/toggle/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        task.refresh_from_db()
        self.assertFalse(task.completed)

    def test_delete_own_task(self):
        """An authenticated user can delete their own task."""
        task = self.make_task(self.alice, title="Delete me")
        response = self.alice_client.delete(f"/api/tasks/{task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Task.objects.filter(pk=task.pk).exists())

    def test_delete_other_users_task_returns_404(self):
        """Another user's task cannot be deleted."""
        task = self.make_task(self.alice, title="Alice task")
        response = self.bob_client.delete(f"/api/tasks/{task.pk}/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Task.objects.filter(pk=task.pk).exists())

    def test_unauthenticated_list_rejected(self):
        """Unauthenticated requests are rejected with 401."""
        response = self.anon_client.get("/api/tasks/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_create_rejected(self):
        """Unauthenticated task creation is rejected with 401."""
        response = self.anon_client.post(
            "/api/tasks/", {"title": "Sneaky task"}, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(Task.objects.filter(title="Sneaky task").exists())


class DemoLoginTests(TestCase):
    """One-click demo login (POST /api/auth/demo/).

    Each click creates a fresh demo user seeded with sample tasks, so
    every visitor gets their own isolated task list.
    """

    def setUp(self):
        self.client = APIClient()

    def test_demo_login_returns_jwts_and_seeds_tasks(self):
        """A demo click returns JWTs and seeds a mixed set of tasks."""
        response = self.client.post("/api/auth/demo/", {}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        user = User.objects.get(username__startswith="demo-")
        tasks = list(user.tasks.all())
        self.assertEqual(len(tasks), 4)
        self.assertEqual(len({task.title for task in tasks}), 4)
        self.assertEqual(
            sum(1 for task in tasks if task.completed), 1
        )
        self.assertEqual(
            {task.priority for task in tasks}, {"low", "medium", "high"}
        )

        # The issued access token actually authenticates as the demo user.
        authed = APIClient()
        authed.credentials(
            HTTP_AUTHORIZATION=f"Bearer {response.data['access']}"
        )
        me = authed.get("/api/me/")
        self.assertEqual(me.status_code, status.HTTP_200_OK)
        self.assertEqual(me.data["username"], user.username)

    def test_demo_login_creates_a_fresh_user_each_time(self):
        """Each demo click is its own user with its own tasks."""
        first = self.client.post("/api/auth/demo/", {}, format="json")
        second = self.client.post("/api/auth/demo/", {}, format="json")
        self.assertEqual(first.status_code, status.HTTP_200_OK)
        self.assertEqual(second.status_code, status.HTTP_200_OK)
        self.assertEqual(User.objects.count(), 2)
        usernames = list(User.objects.values_list("username", flat=True))
        self.assertTrue(all(name.startswith("demo-") for name in usernames))
        self.assertNotEqual(usernames[0], usernames[1])
        self.assertEqual(Task.objects.count(), 8)

    def test_demo_users_cannot_see_each_others_tasks(self):
        """One demo visitor's tasks are invisible to the next."""
        first = self.client.post("/api/auth/demo/", {}, format="json")
        second = self.client.post("/api/auth/demo/", {}, format="json")
        first_client = APIClient()
        first_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {first.data['access']}"
        )
        second_client = APIClient()
        second_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {second.data['access']}"
        )
        first_tasks = first_client.get("/api/tasks/")
        second_tasks = second_client.get("/api/tasks/")
        self.assertEqual(len(first_tasks.data), 4)
        self.assertEqual(len(second_tasks.data), 4)
        first_ids = {task["id"] for task in first_tasks.data}
        second_ids = {task["id"] for task in second_tasks.data}
        self.assertTrue(first_ids.isdisjoint(second_ids))

    def test_demo_user_has_no_usable_password(self):
        """A demo account can never sign in via /api/token/ with a password."""
        self.client.post("/api/auth/demo/", {}, format="json")
        user = User.objects.get(username__startswith="demo-")
        self.assertFalse(user.has_usable_password())
        login = self.client.post(
            "/api/token/",
            {"username": user.username, "password": "anything"},
            format="json",
        )
        self.assertEqual(login.status_code, status.HTTP_401_UNAUTHORIZED)
