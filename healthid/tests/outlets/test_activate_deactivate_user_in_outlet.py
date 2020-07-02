import json
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.outlets import \
    activate_deactivate_outlet_user
from healthid.apps.outlets.models import OutletUser


class TestActivateDeactivateOutletUser(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.outlet_user_data = {
            'outlet_id': self.outlet.id,
            'user_id': self.user.id,
            'is_active': json.dumps(True)
        }
        self.outlet_user_data_two = {
            'outlet_id': self.outlet.id,
            'user_id': self.manager.id,
            'is_active': json.dumps(True)
        }

    def test_can_activate_user_in_outlet(self):
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['data']['activateDeactivateOutletUser'])
        self.assertNotIn('errors', response)

    def test_can_deactivate_user_in_outlet(self):
        self.outlet_user_data['is_active'] = json.dumps(False)
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['data']['activateDeactivateOutletUser'])
        self.assertNotIn('errors', response)

    def test_cannot_activate_user_who_isnt_part_of_outlet(self):
        OutletUser.objects.filter(
            user=self.user, outlet=self.outlet).first().delete()
        OutletUser.objects.filter(
            user=self.user, outlet=self.outlet).first().delete()
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['errors'])

    def test_cant_deactivate_when_only_one_user_is_active_in_outlet(self):
        OutletUser.objects.filter(
            user=self.user, outlet=self.outlet).first().delete()
        self.outlet_user_data['is_active'] = json.dumps(False)
        self.outlet_user_data_two['is_active'] = json.dumps(False)
        self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(
                **self.outlet_user_data_two))
        self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.outlet_user_data['user_id'] = self.master_admin_user.id
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['errors'])

    def test_cant_activate_user_active_in_another_outlet(self):
        self.outlet_user_data['user_id'] = self.second_master_admin_user.id
        OutletUser(
            user=self.second_master_admin_user, outlet=self.outlet).save()
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['errors'])

    def test_cant_activate_user_in_outlet_you_dont_belong_to(self):
        self.outlet_user_data['outlet_id'] = self.second_outlet.id
        self.outlet_user_data['user_id'] = self.second_master_admin_user.id
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['errors'])

    def test_cant_activate_user_when_your_not_an_active_user_in_outlet(self):
        outlet_user = OutletUser.objects.get(
            user=self.master_admin_user, outlet=self.outlet)
        outlet_user.is_active_outlet = False
        outlet_user.save()
        response = self.query_with_token(
            self.access_token_master,
            activate_deactivate_outlet_user.format(**self.outlet_user_data))
        self.assertIsNotNone(response['errors'])
