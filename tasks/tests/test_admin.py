from django.contrib.admin.sites import AdminSite
from django.test import TestCase
from django.utils import timezone

from tasks.admin import TaskAdmin, WorkerAdmin
from tasks.models import Position, Task, TaskType, Worker


class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm):
        return True


request = MockRequest()
request.user = MockSuperUser()


class WorkerAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.position = Position.objects.create(name="Developer")
        self.worker_admin = WorkerAdmin(Worker, self.site)

    def test_list_display(self):
        self.assertEqual(
            self.worker_admin.list_display, ("username", "email", "position")
        )


class TaskAdminTest(TestCase):
    def setUp(self):
        self.site = AdminSite()
        self.task_admin = TaskAdmin(Task, self.site)
        self.task_type = TaskType.objects.create(name="Bug")
        self.position = Position.objects.create(name="QA")
        self.worker = Worker.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
            position=self.position,
        )

    def test_list_display(self):
        self.assertEqual(
            self.task_admin.list_display, ("title", "priority", "task_type", "deadline")
        )

    def test_filter_horizontal(self):
        self.assertEqual(self.task_admin.filter_horizontal, ("assignees",))

    def test_get_queryset(self):
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            deadline=timezone.now() + timezone.timedelta(days=365),
            priority="HIGH",
            task_type=self.task_type,
            created_by=self.worker,
        )
        queryset = self.task_admin.get_queryset(request)
        self.assertIn(task, queryset)


class AdminRegistrationTest(TestCase):
    def test_models_registered(self):
        from django.contrib.admin.sites import site

        self.assertTrue(site.is_registered(Position))
        self.assertTrue(site.is_registered(TaskType))
        self.assertTrue(site.is_registered(Worker))
        self.assertTrue(site.is_registered(Task))
