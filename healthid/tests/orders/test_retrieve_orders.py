from healthid.tests.base_config import BaseConfiguration
from healthid.tests.test_fixtures.orders import (
    retrieve_orders, retrieve_order, retrieve_open_orders,
    retrieve_closed_orders, retrieve_orders_default_paginated,
    retrieve_open_orders_default_paginated,
    retrieve_closed_orders_default_paginated,
    retrieve_orders_custom_paginated, retrieve_open_orders_custom_paginated,
    retrieve_closed_orders_custom_paginated
)
from healthid.tests.factories import OrderFactory


class TestRetrieveOrders(BaseConfiguration):
    def test_user_can_retrieve_orders(self):
        response = self.query_with_token(self.access_token, retrieve_orders)
        self.assertIsNotNone(response['data']['orders'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_single_order(self):
        response = self.query_with_token(
            self.access_token, retrieve_order.format(order_id=self.order.id))
        self.assertIsNotNone(response['data']['order'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_open_orders(self):
        response = self.query_with_token(
            self.access_token, retrieve_open_orders.format(status="Open"))
        self.assertIsNotNone(response['data']['ordersSortedByStatus'])
        self.assertNotIn('errors', response)

    def test_user_can_retrieve_closed_orders(self):
        response = self.query_with_token(
            self.access_token, retrieve_closed_orders)
        self.assertIsNotNone(response['data']['closedOrders'])
        self.assertNotIn('errors', response)

    def test_retrieve_orders_default_paginated(self):
        OrderFactory.create_batch(size=10)
        response = self.query_with_token(
            self.access_token,
            retrieve_orders_default_paginated
        )
        self.assertEqual(response["data"]["totalOrdersPagesCount"], 1)

    def test_retrieve_open_orders_default_paginated(self):
        OrderFactory.create_batch(size=15)
        response = self.query_with_token(
            self.access_token,
            retrieve_open_orders_default_paginated.format(status="Open")
        )
        self.assertEqual(response["data"]["totalOrdersPagesCount"], 1)

    def test_retrieve_closed_orders_default_paginated(self):
        OrderFactory.create_batch(size=15, closed=True)
        response = self.query_with_token(
            self.access_token,
            retrieve_closed_orders_default_paginated
        )
        self.assertEqual(response["data"]["totalOrdersPagesCount"], 1)

    def test_retrieve_orders_custom_paginated(self):
        OrderFactory.create_batch(size=14)
        response = self.query_with_token(
            self.access_token,
            retrieve_orders_custom_paginated.format(pageCount=5, pageNumber=1)
        )
        self.assertEqual(response["data"]["totalOrdersPagesCount"], 3)

    def test_retrieve_open_orders_custom_paginated(self):
        OrderFactory.create_batch(size=14)
        response = self.query_with_token(
            self.access_token,
            retrieve_open_orders_custom_paginated.format(
                pageCount=5, pageNumber=1, status="Open")
        )
        self.assertEqual(response["data"]["totalOrdersPagesCount"], 1)

    def test_retrieve_closed_orders_custom_paginated(self):
        OrderFactory.create_batch(size=14, closed=True)
        response = self.query_with_token(
            self.access_token,
            retrieve_closed_orders_custom_paginated.format(
                pageCount=5, pageNumber=1)
        )
        self.assertEqual(response["data"]["totalOrdersPagesCount"], 3)
