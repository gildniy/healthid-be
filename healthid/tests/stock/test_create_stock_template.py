from django.core import mail

from healthid.apps.notifications.models import Notification
from healthid.apps.stock.models import StockCountTemplate
from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.stock import (
    create_stock_template_string,
    delete_stock_template_string,
    edit_stock_template_string,
    query_all_templates,
    query_single_template
)
from healthid.utils.stock_utils.stock_count_alert import \
    generate_stock_counts_notifications
from healthid.utils.messages.common_responses import SUCCESS_RESPONSES


class StockTemplateTestCase(BaseConfiguration):
    def setUp(self):
        super().setUp()
        self.product_id1 = self.create_product(product_name='panadol').id
        self.product_id2 = self.create_product(product_name='hedex').id
        self.user_id1 = self.register_user(self.stock_count_user1).id
        self.user_id2 = self.register_user(self.stock_count_user2).id
        self.outlet_id = self.outlet.id
        self.event_type_id = self.event.event_type.id
        self.start_date = self.event.start_date.date()
        self.end_date = self.event.end_date.date()
        self.end_on = self.event.end_date.date()
        self.stock_template_data = {
            'product_ids': f'[{self.product_id1}, {self.product_id2}]',
            'assigned_user_ids': f'["{self.user_id1}", "{self.user_id2}"]',
            'dessignate_user_ids': f'["{self.user_id1}", "{self.user_id2}"]',
            'outlet_id': self.outlet_id,
            'event_type_id': f'"{self.event_type_id}"',
            'start_date': f'"{self.start_date}"',
            'end_date': f'"{self.end_date}"',
            'end_on': f'"{self.end_on}"',
            'interval': 0
        }

    def create_stock_template(self):
        response = self.query_with_token(
            self.access_token_master,
            create_stock_template_string.format(**self.stock_template_data)
        )
        return response

    def test_stock_template_model(self):
        template = StockCountTemplate()
        template.save()
        self.assertEqual(str(template.id), str(template))

    def test_create_stock_template(self):
        response = self.create_stock_template()

        self.assertEqual(SUCCESS_RESPONSES[
                         "creation_success"].format("Stock count template"),
                         response['data']['createStockCountTemplate']
                         ['success'])
        self.assertEqual(len(mail.outbox), 1)

    def test_edit_stock_template(self):
        response = self.create_stock_template()
        template_id =\
            response['data']['createStockCountTemplate']['stockTemplate']['id']
        response = self.query_with_token(
            self.access_token_master,
            edit_stock_template_string.format(
                **self.stock_template_data, template_id=template_id)
        )
        self.assertEqual(SUCCESS_RESPONSES[
                         "edit_success"].format("Stock count template"),
                         response['data']['editStockCountTemplate']
                         ['success'])
        self.assertEqual(len(mail.outbox), 2)

    def test_delete_stock_template(self):
        response = self.create_stock_template()
        template_id =\
            response['data']['createStockCountTemplate']['stockTemplate']['id']
        response = self.query_with_token(
            self.access_token_master,
            delete_stock_template_string.format(id=template_id)
        )
        self.assertEqual(SUCCESS_RESPONSES[
                         "deletion_success"].format("Stock template"),
                         response['data']['deleteStockCountTemplate']
                         ['success'])

    def test_fetch_all_stock_templates(self):
        self.create_stock_template()
        self.create_stock_template()
        response = self.query_with_token(
            self.access_token_master,
            query_all_templates.format(outlet_id=self.outlet_id)
        )
        self.assertEqual(2, len(response['data']['stockTemplates']))

    def test_fetch_single_stock_templates(self):
        template = self.create_stock_template()
        template_id = \
            template['data']['createStockCountTemplate']['stockTemplate']['id']
        response = self.query_with_token(
            self.access_token_master,
            query_single_template.format(
                outlet_id=self.outlet_id, template_id=template_id)
        )
        self.assertIn('products', response['data']['stockTemplate'])

    def test_generate_stock_counts_notifications(self):
        self.create_stock_template()
        generate_stock_counts_notifications()
        notifications = Notification.objects.all()
        self.assertTrue(len(notifications) >= 1)
