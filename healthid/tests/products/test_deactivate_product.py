from healthid.tests.test_fixtures.products import (
    deactivate_product, retrieve_deactivated_products, activate_product)
from healthid.tests.products.test_create_product import TestCreateProduct
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES


class TestDeactivateProducts(TestCreateProduct):
    def deactivate_another_product(self):
        '''
        Method to deactivate a product
        '''
        self.product.is_active = False
        return self.product.save()

    def test_master_admin_can_deactivate_product(self):
        '''
        Method tests master admin can deactivate products
        '''
        response = self.query_with_token(self.access_token_master,
                                         deactivate_product([self.product.id]))
        self.assertIn("success", response["data"]["deactivateProduct"])
        self.assertNotIn('errors', response)

    def test_managers_or_all_users_cannot_deactivate_product(self):
        '''
        Method tests managerss and other users can not deactivate
        products
        '''
        response = self.query_with_token(self.access_token,
                                         deactivate_product([self.product.id]))
        self.assertIsNotNone(response['errors'])

    def test_cannot_deactivate_products_without_product_ids(self):
        '''
        Method tests an error is raised if a list of empty ids is
        provided
        '''
        response = self.query_with_token(self.access_token_master,
                                         deactivate_product([]))
        self.assertEqual(response['errors'][0]['message'],
                         'Please provide product ids.')

    def test_cannot_deactivate_product_that_does_not_exist(self):
        '''
        Method tests an error is rasied if a product does not exist
        '''
        response = self.query_with_token(self.access_token_master,
                                         deactivate_product([101]))
        self.assertEqual(response['errors'][0]['message'],
                         "Product with id [101] does not exist or is "
                         "already deactivated.")

    def test_cannot_deactivate_product_when_unauthenticated(self):
        '''
        Method tests unauthenticated user cannot deactivate products
        '''
        response = self.query_with_token('',
                                         deactivate_product([self.product.id]))
        self.assertIsNotNone(response['errors'])

    def test_master_admin_can_retrieve_deactivated_products(self):
        '''
        Tests master admin can retrieve deactivated products
        '''
        self.deactivate_another_product()
        response = self.query_with_token(
            self.access_token_master,
            retrieve_deactivated_products(self.outlet.id))
        self.assertEqual(response['data']['deactivatedProducts'][0]['id'],
                         str(self.product.id))

    def test_managers_or_all_users_cannot_retrieve_deactivated_products(self):
        '''
        Tests managers and other users cannot retrieve deactivated
        products
        '''
        response = self.query_with_token(
            self.access_token,
            retrieve_deactivated_products(self.outlet.id))
        self.assertIsNotNone(response['errors'])

    def test_cannot_retrieve_deactivated_products_when_unauthenticated(self):
        '''
        Tests unauthenticated user cannot retrieve deactivated products
        '''
        response = self.query_with_token(
            '', retrieve_deactivated_products(self.outlet.id))
        self.assertIsNotNone(response['errors'])

    def test_master_admin_can_activate_product(self):
        '''
        Method tests master admin can activate products
        '''
        self.deactivate_another_product()
        response = self.query_with_token(
            self.access_token_master,
            activate_product([self.product.id])
        )
        self.assertIn("success", response["data"]["activateProduct"])
        self.assertNotIn('errors', response)

    def test_managers_or_all_users_cannot_activate_product(self):
        '''
        Method tests managerss and other users can not activate
        products
        '''
        self.deactivate_another_product()
        response = self.query_with_token(
            self.access_token,
            activate_product([self.product.id])
        )
        self.assertIsNotNone(response['errors'])

    def test_cannot_activate_products_without_product_ids(self):
        '''
        Method tests an error is raised if a list of empty ids is
        provided
        '''
        self.deactivate_another_product()
        response = self.query_with_token(self.access_token_master,
                                         activate_product([]))
        self.assertEqual(response['errors'][0]['message'],
                         'Please provide product ids.')

    def test_cannot_activate_product_that_does_not_exist(self):
        '''
        Method tests an error is rasied if a product does not exist
        '''
        self.deactivate_another_product()
        response = self.query_with_token(self.access_token_master,
                                         activate_product([101]))
        self.assertEqual(response['errors'][0]['message'],
                         PRODUCTS_ERROR_RESPONSES[
                         "product_activation_error"].format("[101]"))

    def test_cannot_activate_product_when_unauthenticated(self):
        '''
        Method tests unauthenticated user cannot activate products
        '''
        self.deactivate_another_product()
        response = self.query_with_token(
            '', activate_product([self.product.id])
        )
        self.assertIsNotNone(response['errors'])
