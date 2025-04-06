from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from tasks.models import Task, TaskType

User = get_user_model()


class IndexViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com"
        )
        self.client.login(username="testuser", password="testpass123")
        self.task_type = TaskType.objects.create(name="Bug")
        self.task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            deadline=timezone.now() + timezone.timedelta(days=3),
            priority="HIGH",
            task_type=self.task_type,
            created_by=self.user,
        )
        self.task.assignees.add(self.user)

    def test_index_view_context(self):
        response = self.client.get(reverse("tasks:index"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("assigned_tasks", response.context)
        self.assertEqual(response.context["total_tasks"], 1)
        self.assertEqual(response.context["completed_tasks"], 0)
        self.assertEqual(response.context["overdue_tasks"], 0)


class TaskListViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user",
            password="pass",
            email="user@example.com"
        )
        self.client.login(username="user", password="pass")
        self.task_type = TaskType.objects.create(name="Feature")
        self.task = Task.objects.create(
            title="Task 1",
            description="Description",
            deadline=timezone.now(),
            priority="MEDIUM",
            task_type=self.task_type,
            created_by=self.user,
        )
        self.task.assignees.add(self.user)

    def test_task_list_filtering(self):
        response = self.client.get(reverse("tasks:task-list") + "?search=Task")
        self.assertContains(response, "Task 1")

        response = self.client.get(reverse("tasks:task-list") + "?status=active")
        self.assertEqual(len(response.context["tasks"]), 1)

        response = self.client.get(reverse("tasks:task-list") + "?priority=MEDIUM")
        self.assertEqual(response.context["tasks"][0].priority, "MEDIUM")


class TaskCreateUpdateDeleteTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="admin",
            password="adminpass",
            email="admin@example.com"
        )
        self.client.login(username="admin", password="adminpass")
        self.task_type = TaskType.objects.create(name="Refactoring")
        self.worker = User.objects.create_user(
            username="worker",
            password="workerpass",
            email="worker@example.com"
        )

    def test_task_creation(self):
        response = self.client.post(
            reverse("tasks:task-create"),
            {
                "title": "New Task",
                "description": "Details",
                "deadline": timezone.now() + timezone.timedelta(days=365),
                "priority": "LOW",
                "task_type": self.task_type.id,
                "assignees": [self.worker.id],
            },
        )
        self.assertRedirects(response, reverse("tasks:task-list"))
        self.assertEqual(Task.objects.count(), 1)

    def test_task_update(self):
        task = Task.objects.create(
            title="Old Title",
            created_by=self.user,
            deadline=timezone.now(),
            priority="HIGH",
            task_type=self.task_type,
        )
        response = self.client.post(
            reverse("tasks:task-update", kwargs={"pk": task.pk}),
            {
                "title": "Updated Title",
                "description": "New Description",
                "deadline": timezone.now() + timezone.timedelta(days=365),
                "priority": "LOW",
                "task_type": self.task_type.id,
                "assignees": [self.worker.id],
            },
        )
        self.assertRedirects(response, reverse("tasks:task-list"))
        task.refresh_from_db()
        self.assertEqual(task.title, "Updated Title")

    def test_task_delete(self):
        task = Task.objects.create(
            title="To Delete",
            created_by=self.user,
            deadline=timezone.now(),
            priority="MEDIUM",
            task_type=self.task_type,
        )
        response = self.client.post(reverse("tasks:task-delete", kwargs={"pk": task.pk}))
        self.assertRedirects(response, reverse("tasks:task-list"))
        self.assertEqual(Task.objects.count(), 0)
