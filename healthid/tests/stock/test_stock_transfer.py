from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.stock import (
    open_stock_transfer, view_stock_transfers, close_stock_transfer,
    view_stock_transfer)
from healthid.utils.messages.stock_responses import\
     STOCK_SUCCESS_RESPONSES, STOCK_ERROR_RESPONSES


class TestStockTransfer(BaseConfiguration):
    """Test class to test stock transfer mutations and queries
    """
    def setUp(self):
        super().setUp()

        self.stock_transfer_params = {
            "batch_ids": self.batch_info.id,
            "outlet_id": self.outlet.id,
            "product_id": self.product.id,
            "quantity": 4
        }

    def test_open_stock_transfer_with_vague_quantity(self):
        """Method to test that a stock transfer can't be opened with higher
        transfer quantity than the available quantity.
        """
        self.stock_transfer_params['quantity'] = 400
        wrong_quantity = self.stock_transfer_params['quantity']
        response = self.query_with_token(
            self.second_master_admin_token,
            open_stock_transfer.format(**self.stock_transfer_params))
        self.assertEqual(
            response['errors'][0]['message'],
            f"Can't transfer batches with ids ['{self.batch_info.id}'] \
since quantities [{wrong_quantity}] are above the available quantity!")

    def test_open_stock_transfer(self):
        """Method to test that a stock transfer can be opened
        """
        response = self.query_with_token(
            self.second_master_admin_token,
            open_stock_transfer.format(**self.stock_transfer_params))
        self.assertEqual(response['data']['openStockTransfer']['success'][0],
                         STOCK_SUCCESS_RESPONSES[
                                           "stock_transfer_open_success"])

    def test_close_transfer(self):
        """Test that a user can mark a transfer as closed
        """
        response = self.query_with_token(
            self.second_master_admin_token,
            open_stock_transfer.format(**self.stock_transfer_params))
        close_transer_params = {
            'transfer_number': response['data'][
                'openStockTransfer']['stockTransfer']['id'],
            'outlet_id': self.outlet.id
        }
        response = self.query_with_token(
            self.access_token, close_stock_transfer.format(
                **close_transer_params))

        self.assertEqual(response['data']['closeStockTransfer']['success'],
                         STOCK_SUCCESS_RESPONSES[
                              "stock_transfer_close_success"])

    def test_view_stock_transfers(self):
        """Test that user can view stock transfers
        """
        self.query_with_token(self.second_master_admin_token,
                              open_stock_transfer.format(
                                  **self.stock_transfer_params))
        response = self.query_with_token(
            self.access_token, view_stock_transfers)
        self.assertNotIn('errors', response)

    def test_open_stock_transfer_same_outlet(self):
        """Method to test that a stock transfer can't be opened
        to the same outlet that the user belongs to
        """
        response = self.query_with_token(
            self.access_token_master,
            open_stock_transfer.format(**self.stock_transfer_params))
        self.assertEqual(response['errors'][0]['message'],
                         STOCK_ERROR_RESPONSES["same_origin_stock_transfer"])

    def test_open_stock_transfer_vague_products(self):
        """Method to test that a stock transfer can't be opened
        with vague products
        """
        response = self.query_with_token(
            self.second_master_admin_token,
            open_stock_transfer.format(**self.stock_transfer_params))
        close_transer_params = {
            'transfer_number': "qwertyu123"
        }
        response = self.query_with_token(
            self.access_token, close_stock_transfer.format(
                **close_transer_params))

        self.assertEqual(response['errors'][0]['message'],
                         STOCK_ERROR_RESPONSES["close_transfer_error"])

    def test_view_stock_transfer(self):
        """Test that user can view a single stock transfer
        """
        response = self.query_with_token(
            self.second_master_admin_token,
            open_stock_transfer.format(
                **self.stock_transfer_params))
        params = {
            'transfer_number': response['data'][
                'openStockTransfer']['stockTransfer']['id']
        }
        response = self.query_with_token(
            self.access_token, view_stock_transfer.format(**params))
        self.assertNotIn('errors', response)
