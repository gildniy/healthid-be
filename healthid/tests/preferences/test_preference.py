from django.test import TestCase
from healthid.apps.preference.apps import PreferenceConfig


class PreferenceTest(TestCase):
    def test_app_config(self):
        self.assertEqual('preference', PreferenceConfig.name)
