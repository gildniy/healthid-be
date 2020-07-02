from healthid.apps.receipts.models import ReceiptTemplate
from healthid.tests.receipts.base import ReceiptBaseCase
from healthid.tests.test_fixtures.template import (create_template,
                                                   delete_template,
                                                   query_template,
                                                   update_template)
from healthid.tests.test_fixtures.fieldset import \
    retrieve_receipt, retrieve_receipts


class ReceiptTestCase(ReceiptBaseCase):

    def test_empty_db(self):
        resp = self.query_with_token(
            self.access_token_master,
            '{receiptTemplates{id}}')
        self.assertResponseNoErrors(resp, {'receiptTemplates': []})

    def test_single_receipt_template(self):
        template = self.create_receipt_template()
        resp = self.query_with_token(
            self.access_token_master,
            query_template(template.id))
        self.assertResponseNoErrors(
            resp, {"receiptTemplate": {"id": template.id}})

    def test_create_receipt_template(self):
        outlet = self.outlet
        response = self.query_with_token(
            self.access_token_master,
            create_template(outlet.id),
        )
        self.assertResponseNoErrors(
            response, {"createReceiptTemplate": {
                'receiptTemplate': {'cashier': False}
            }})

    def test_update_template(self):
        template = self.create_receipt_template()
        response = self.query_with_token(
            self.access_token_master,
            update_template(template.id),
        )
        self.assertResponseNoErrors(
            response, {"updateReceiptTemplate": {
                'receiptTemplate': {
                    'id': template.id, 'cashier': True, 'discountTotal': True
                }
            }})

    def test_receipt_model(self):
        template = self.create_receipt_template()
        all_receipts = ReceiptTemplate.objects.all()
        self.assertQuerysetEqual(
            all_receipts, [f'<ReceiptTemplate: {template.id}>'])

    def test_delete_receipt(self):
        template = self.create_receipt_template()
        response = self.query_with_token(
            self.access_token_master,
            delete_template(template.id),)
        self.assertIn("success", response["data"]["deleteReceiptTemplate"])

    def test_user_can_retrieve_receipts(self):
        response = self.query_with_token(self.access_token, retrieve_receipts)
        self.assertIsNotNone(response['data']['receipts'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_single_receipt(self):
        receipt = self.create_fieldset()
        response = self.query_with_token(
            self.access_token, retrieve_receipt.format(receipt_id=receipt.id))
        self.assertIsNotNone(response['data']['receipt'])
        self.assertNotIn('errors', response)
