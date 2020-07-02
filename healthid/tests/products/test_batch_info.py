from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.batch_info \
    import batch_info_query, update_batch_info, \
    query_product_batch_info, single_batch_info, \
    all_batch_info, delete_batch_info, near_expired_batches
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class TestBatchInfo(BaseConfiguration):
    """
    Testing Adding user by the Master Admin
    """

    def setUp(self):
        super().setUp()
        self.batch_data = {
            'product_id': self.product.id,
            'supplier_id': self.supplier.id,
            'expiry_date': '2020-02-10'
        }

    def test_add_batch_info(self):
        """
        test batch info creation
        """
        resp = self.query_with_token(
            self.access_token, batch_info_query.format(**self.batch_data))
        self.assertIn('data', resp)
        self.assertEqual(
            resp['data']['createBatchInfo']['batchInfo']['supplier']['name'],
            self.supplier.name)
        self.assertEqual(
            resp['data']['createBatchInfo']['batchInfo']['outlet']['id'],
            '1')

    def test_update_batch(self):
        """
        Test if batch can be updated.
        """
        self.batch_data['batch_id'] = self.batch_info.id
        resp = self.query_with_token(
            self.access_token_master,
            update_batch_info.format(**self.batch_data))

        self.assertIn('data', resp)
        self.assertEqual(
            resp['data']['updateBatchInfo']['batchInfo']['supplier']['name'],
            self.supplier.name)
        self.assertEqual(
            resp['data']['updateBatchInfo']['batchInfo']['batchNo'],
            self.batch_info.batch_no)
        self.assertEqual(
            resp['data']['updateBatchInfo']['batchInfo']['batchQuantities'][
                0]['quantityRemaining'],
            33)

    def test_product_batches(self):
        product_data = {'product_id': self.product.id}
        resp = self.query_with_token(
            self.access_token, query_product_batch_info.format(**product_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['productBatchInfo'][0]['batchNo'],
                         self.batch_info.batch_no)

    def test_single_batch_info(self):
        product_data = {'batch_id': self.batch_info.id}
        resp = self.query_with_token(self.access_token,
                                     single_batch_info.format(**product_data))
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['batchInfo']['batchNo'],
                         self.batch_info.batch_no)

    def test_all_batch_info(self):
        resp = self.query_with_token(self.access_token, all_batch_info)
        self.assertIn('data', resp)
        self.assertEqual(resp['data']['allBatchInfo'][0]['batchNo'],
                         self.batch_info.batch_no)

    def test_invalid_date_format(self):
        """
        test wrong date format
        """
        date_field = 'expiry_date'
        self.batch_data['expiry_date'] = date_field
        resp = self.query_with_token(
            self.access_token, batch_info_query.format(**self.batch_data))
        self.assertIn(
            'invalid literal',
            resp['errors'][0]['message'])

    def test_invalid_batch_info_id(self):
        """
        test wrong batch info id
        """
        batch_info_id = '12121212121'
        self.batch_data['batch_id'] = batch_info_id
        resp = self.query_with_token(
            self.access_token_master,
            update_batch_info.format(**self.batch_data))

        self.assertIn('data', resp)
        self.assertIn(PRODUCTS_ERROR_RESPONSES[
                          "inexistent_batchinfo"].format(batch_info_id),
                      resp['errors'][0]['message'])

    def test_delete_batch_info(self):
        batch_info = {'batch_id': self.batch_info.id}
        resp = self.query_with_token(self.access_token_master,
                                     delete_batch_info.format(**batch_info))
        self.assertIn('data', resp)

    def test_near_expired_batches(self):
        response = self.query_with_token(
            self.access_token, near_expired_batches)
        self.assertIn('nearExpiredBatches', response['data'])
