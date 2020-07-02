from django.test import TestCase
from healthid.apps.authentication.models import Role


class RoleModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.role = Role.objects.create(name="Master Admin")

    def test_role_creation(self):
        self.assertEquals(self.role.name, "Master Admin")
