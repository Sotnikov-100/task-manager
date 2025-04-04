from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from tasks.forms import TaskForm, WorkerCreationForm
from tasks.models import Position, Task, TaskType, Worker

User = get_user_model()


class WorkerCreationFormTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.valid_data = {
            "username": "testuser",
            "email": "test@example.com",
            "position": self.position.id,
            "password1": "TestPass123!",
            "password2": "TestPass123!",
        }

    def test_form_with_valid_data(self):
        form = WorkerCreationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.position, self.position)

    def test_form_without_email(self):
        invalid_data = self.valid_data.copy()
        invalid_data.pop("email")
        form = WorkerCreationForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_with_duplicate_email(self):
        Worker.objects.create_user(
            username="existinguser",
            email="test@example.com",
            password="pass123",
            position=self.position,
        )
        form = WorkerCreationForm(data=self.valid_data)
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)


class TaskFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="admin", password="adminpass")
        self.position = Position.objects.create(name="QA")
        self.task_type = TaskType.objects.create(name="Bug")
        self.assignee = User.objects.create_user(
            username="worker",
            password="workerpass",
            email="worker@example.com",
            position=self.position,
        )
        self.valid_data = {
            "title": "Fix Bugs",
            "description": "Important fixes",
            "deadline": timezone.now() + timezone.timedelta(days=3),
            "priority": Task.PriorityChoices.HIGH,
            "task_type": self.task_type.id,
            "assignees": [self.assignee.id],
        }

    def test_form_with_valid_data(self):
        form = TaskForm(data=self.valid_data)
        self.assertTrue(form.is_valid())
        task = form.save(commit=False)
        task.created_by = self.user
        task.save()
        form.save_m2m()
        self.assertEqual(task.title, "Fix Bugs")
        self.assertIn(self.assignee, task.assignees.all())
