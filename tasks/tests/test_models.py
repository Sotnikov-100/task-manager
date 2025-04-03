from django.test import TestCase
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
from django.utils import timezone
from tasks.models import Position, TaskType, Worker, Task

class PositionModelTest(TestCase):
    def test_position_creation(self):
        position = Position.objects.create(name="Developer")
        self.assertEqual(str(position), "Developer")
        self.assertEqual(Position.objects.count(), 1)

    def test_position_unique_name(self):
        Position.objects.create(name="Designer")
        with self.assertRaises(Exception):
            Position.objects.create(name="Designer")

class TaskTypeModelTest(TestCase):
    def test_task_type_creation(self):
        task_type = TaskType.objects.create(name="Bug")
        self.assertEqual(str(task_type), "Bug")
        self.assertEqual(TaskType.objects.count(), 1)

    def test_task_type_unique_name(self):
        TaskType.objects.create(name="Feature")
        with self.assertRaises(Exception):
            TaskType.objects.create(name="Feature")

class WorkerModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="QA")
        self.user = Worker.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
            position=self.position
        )

    def test_worker_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(self.user.email, "test@example.com")
        self.assertEqual(self.user.position.name, "QA")
        self.assertFalse(self.user.is_superuser)

    def test_worker_str_representation(self):
        self.assertEqual(str(self.user), "testuser (QA)")

    def test_worker_email_unique(self):
        with self.assertRaises(Exception):
            Worker.objects.create_user(
                username="anotheruser",
                password="pass123",
                email="test@example.com"
            )

    def test_worker_without_position(self):
        worker = Worker.objects.create_user(
            username="noposition",
            password="testpass",
            email="nopos@example.com"
        )
        self.assertIsNone(worker.position)

class TaskModelTest(TestCase):
    def setUp(self):
        self.position = Position.objects.create(name="Developer")
        self.task_type = TaskType.objects.create(name="Refactoring")
        self.user = Worker.objects.create_user(
            username="creator",
            password="password",
            email="creator@example.com"
        )
        self.assignee = Worker.objects.create_user(
            username="assignee",
            password="assignee_pass",
            email="assignee@example.com"
        )
        self.task = Task.objects.create(
            title="Fix Bugs",
            description="Fix all critical bugs",
            deadline=timezone.now() + timedelta(days=3),  # Використання timezone.now()
            priority=Task.PriorityChoices.HIGH,
            task_type=self.task_type,
            created_by=self.user
        )
        self.task.assignees.add(self.assignee)

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Fix Bugs")
        self.assertEqual(self.task.priority, "HIGH")
        self.assertFalse(self.task.is_completed)
        self.assertEqual(self.task.task_type.name, "Refactoring")
        self.assertEqual(self.task.created_by.username, "creator")
        self.assertEqual(self.task.assignees.count(), 1)
        self.assertIn(self.assignee, self.task.assignees.all())

    def test_task_str_representation(self):
        self.assertEqual(str(self.task), "Fix Bugs")

    def test_task_default_priority(self):
        task = Task.objects.create(
            title="New Task",
            description="Test default priority",
            deadline=timezone.now(),
            created_by=self.user
        )
        self.assertEqual(task.priority, Task.PriorityChoices.MEDIUM)

    def test_task_deadline_in_past_validation(self):
        task = Task(
            title="Invalid Deadline",
            description="Test past deadline",
            deadline=timezone.now() - timedelta(days=1),
            created_by=self.user
        )
        task.full_clean()

    def test_task_created_at_auto_now_add(self):
        task = Task.objects.get(id=self.task.id)
        self.assertIsNotNone(task.created_at)

    def test_on_delete_position_set_null(self):
        self.position.delete()
        self.user.refresh_from_db()
        self.assertIsNone(self.user.position)

    def test_on_delete_task_type_set_null(self):
        self.task_type.delete()
        self.task.refresh_from_db()
        self.assertIsNone(self.task.task_type)

    def test_on_delete_created_by_cascade(self):
        self.user.delete()
        with self.assertRaises(Task.DoesNotExist):
            Task.objects.get(id=self.task.id)
