from healthid.apps.products.models import Product
from graphql.error import GraphQLError
from healthid.apps.orders.models.orders import OrderDetails
from healthid.utils.app_utils.database import get_model_object


class AddOrderDetails:
    @staticmethod
    def check_list_length(list1, list2, **kwargs):
        """
        Check if the length of two lists are equal

        Args:
            list1: the first lisst
            list2: the second list

        Raises:
            msg(str): error message to show that the list aren't equal
        """
        name1 = kwargs.get('name1')
        name2 = kwargs.get('name2')
        if len(list1) != len(list2):
            msg = f'{name1} list is not equal to {name2} list!'
            raise GraphQLError(msg)

    @classmethod
    def check_product_exists(self, product_list):
        """
        checks that the product ids exist in the database

        Arguments:
            product_list(list): product ids

        Returns:
            list: product ids that exist in the database or raises an
                  error if there is one that doesn't exist in the
                  database
        """
        products = []
        for product_id in product_list:
            product = get_model_object(Product, 'id', product_id)
            products.append(product.id)
        return products

    @classmethod
    def add_supplier(cls, kwargs, supplier, detail_objects):
        """
        attaches a user specified supplier to an order detail

        Arguments:
            kwargs(dict): contains products being ordered and order id
            supplier(iter): iterable of suppliers whose order details are
                      being created
            detail_objects(list): list of 'OrderDetail' model objects
                                  to be saved

        Returns:
            created_order(obj): latest order detail created
        """

        products_list = kwargs.get('products')
        cls.check_product_exists(products_list)
        order_id = kwargs.get('order_id')
        created_order = OrderDetails.check_if_duplicate(
            order_id,
            detail_objects,
            supplier
        )

        return created_order

    @classmethod
    def supplier_autofill(cls, kwargs, detail_objects):
        """
        attaches a default preferred supplier to an order detail

        Arguments:
            kwargs(dict): contains products being ordered and order id
            detail_objects(list): list of 'OrderDetail' model objects
                                  to be saved

        Returns:
            created_order(obj): latest order detail created
        """
        products_list = kwargs.get('products')
        cls.check_product_exists(products_list)
        order_id = kwargs.get('order_id')
        created_order = OrderDetails.check_if_duplicate(
            order_id,
            detail_objects
        )
        return created_order

    @classmethod
    def get_order_details(
        cls, kwargs, order, quantity=None,
        price=None, cost_per_item=None
    ):
        """
        intitalizes order details for an order

        Arguments:
            kwargs(dict): contains products being ordered
            order(obj): whose order details will be intialized
            quantity: either an iterable for quantities of being
                      attached to order details or None if quantities
                      are being autofilled
            price: either an iterable for prices of being attached to
                    to order details or None if it is only creating
                    order detail without price

        Returns:
            list: objects of order details that have been initialized
        """
        products_list = kwargs.get('products')
        products = cls.check_product_exists(products_list)
        object_list = list()  # list to hold order details instances
        for product_id in products:
            product = \
                get_model_object(Product, 'id', product_id)
            order_details = OrderDetails()
            order_details.order = order
            order_details.product = product
            if not quantity:
                order_details.ordered_quantity = product.product_quantity
            else:
                order_details.ordered_quantity = next(quantity)
            if price:
                order_details.price = next(price)
            else:
                order_details.price = ""
            if cost_per_item:
                order_details.cost_per_item = next(cost_per_item)
            else:
                order_details.cost_per_item = ""
            object_list.append(order_details)
        return object_list

    @classmethod
    def add_product_quantity(cls, object_list):
        """
        creates multiple order details at once

        Arguments:
            object_list(list): order details objects

        Returns:
            queryset: order details that have been created
        """
        return OrderDetails.objects.bulk_create(object_list)


add_order_details = AddOrderDetails()
