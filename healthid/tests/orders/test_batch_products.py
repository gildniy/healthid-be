from healthid.tests.base_config import BaseConfiguration
from healthid.utils.messages.products_responses import PRODUCTS_ERROR_RESPONSES
from healthid.tests.factories import (OrderFactory, UserFactory, SuppliersFactory, ProductFactory)
from healthid.tests.test_fixtures.orders \
    import get_all_batch_products, create_batch_product,\
            delete_batch_product, update_batch_product, add_order_items
from django.test import TestCase

class TestBatchProduct(BaseConfiguration):
    """
    Testing batch product feature
    """

    def setUp(self):
        super(TestBatchProduct, self).setUp()
        self.user1 = UserFactory()
        self.order1 = OrderFactory()
        self.supplier1 = SuppliersFactory(user=self.user1)
        self.product1 = ProductFactory()
        self.product2 = ProductFactory()


        self.batch_data = {
            'order_id':self.order1.id,
            'supplier_id':self.supplier1.id,
            'product_id':self.product1.id,
            'product_ids':[self.product1.id, self.product2.id],
            'quantity':10,
            'updated_quantity':11,
            'message': 'Batch, created successfully!',
            'deleteMessage': 'Batches, deleted successfully!'
        }
    
    def test_order_items(self):
        '''
        test the creation of order items 
        '''
        resp = self.query_with_token(
            self.access_token, add_order_items.format(**self.batch_data)
        )
        self.assertEqual(
            len(resp['data']['addOrderItems']['addedProductDetails']),
            len(self.batch_data['product_ids'])
        )

    def test_create_batch_product(self):
        '''
        test create batch product
        '''
        resp = self.query_with_token(
            self.access_token, create_batch_product.format(**self.batch_data)
        )
        resp_message=resp['data']['createProductBatch']['message']
        self.assertEqual(
            resp_message,
            self.batch_data['message'])
    

    def test_get_batch_products(self):
        '''
        test get batch products
        '''
        self.query_with_token(
            self.access_token, create_batch_product.format(**self.batch_data)
        )
        resp = self.query_with_token(
            self.access_token, get_all_batch_products
        )
        self.assertEqual(
            resp['data']['allProductBatch'][0]['quantity'],
            self.batch_data['quantity']
        )
    

    def test_update_batch_products(self):
        '''
        test update product
        '''
        self.query_with_token(
            self.access_token, create_batch_product.format(**self.batch_data)
        )
        resp = self.query_with_token(
            self.access_token, get_all_batch_products
        )
        id = resp['data']['allProductBatch'][0]['id']
        test_data={'batch_id':id, 'quantity':self.batch_data['updated_quantity']}
        resp = self.query_with_token(
            self.access_token, 
            update_batch_product.format(**test_data)
        )
        self.assertEqual(
            resp['data']['updateProductBatch']['productBatchesUpdated'][0]['quantity'],
            self.batch_data['updated_quantity']
        )
    
    
    def test_delete_batch_products(self):
        '''
        test update product
        '''
        self.query_with_token(
            self.access_token, create_batch_product.format(**self.batch_data)
        )
        resp = self.query_with_token(
            self.access_token, get_all_batch_products
        )
        id = resp['data']['allProductBatch'][0]['id']
        resp = self.query_with_token(
            self.access_token, 
            delete_batch_product.format(batch_id=id)
        )
        self.assertEqual(
            resp['data']['deleteProductBatch']['message'],
            self.batch_data['deleteMessage']
        )



        
