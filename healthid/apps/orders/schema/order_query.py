import graphene
import json, logging
from collections import namedtuple, Counter
from graphene_django import DjangoObjectType
from graphql import GraphQLError
from graphql_jwt.decorators import login_required
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.apps.orders.models.orders import (
    SupplierOrderDetails, Order, OrderDetails, OrdersProducts,
    ProductBatch, SupplierOrder
)
from healthid.apps.outlets.models import OutletUser
from healthid.apps.orders.schema.suppliers_query import (
    SuppliersType)
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.orders.models.suppliers import Suppliers
from healthid.utils.app_utils.pagination import pagination_query
from healthid.utils.app_utils.pagination_defaults import PAGINATION_DEFAULT
from healthid.utils.orders_utils.inventory_notification import \
    autosuggest_product_order
from healthid.utils.app_utils.check_user_in_outlet import \
    check_user_has_an_active_outlet
from healthid.utils.app_utils.get_user_business import get_user_business
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES


class SupplierOrderFormOutput(graphene.ObjectType):
    supplier_order_form_id = graphene.String()
    order_id = graphene.Int()
    supplier_id = graphene.String()
    order_name = graphene.String()
    order_number = graphene.String()
    status = graphene.String()
    supplier_order_name = graphene.String()
    supplier_order_number = graphene.String()
    number_of_products = graphene.Int()
    marked_as_sent = graphene.Boolean()


class SupplierOrderInputType(graphene.InputObjectType):
    supplier_order_id = graphene.Int()


class ProductBatchType(DjangoObjectType):
    preferred_supplier = graphene.Field(SuppliersType)
    backup_supplier = graphene.Field(SuppliersType)

    class Meta:
        model = ProductBatch

    def resolve_preferred_supplier(self, info):
        return self.get_preferred_supplier

    def resolve_backup_supplier(self, info):
        return self.get_backup_supplier


class AutosuggestOrder(graphene.ObjectType):
    product_name = graphene.String()
    suggested_quantity = graphene.String()


class OrderType(DjangoObjectType):
    outlet = graphene.String()
    order_items = graphene.List(ProductBatchType)

    class Meta:
        model = Order

    def resolve_outlet(self, info):
        return self.name

    def resolve_order_items(self, info):
        return self.order_items()


class OrderDetailsType(DjangoObjectType):
    class Meta:
        model = OrderDetails


class OrderProductsType(DjangoObjectType):
    class Meta:
        model = OrdersProducts


class SupplierOrderType(DjangoObjectType):
    order_details = graphene.List(ProductBatchType)
    number_of_products = graphene.Int()
    supplier_order_name = graphene.String()
    supplier_order_number = graphene.String()
    deliver_to = graphene.String()
    delivery_due = graphene.Date()
    payment_due = graphene.Date()

    class Meta:
        model = SupplierOrder

    def resolve_number_of_products(self, info):
        return len(self.get_product_batches())

    def resolve_order_details(self, info, **kwargs):
        """
        get order details

        Returns:
            list: order details of a particular supplier and order
        """
        return self.get_product_batches()

    def resolve_supplier_order_name(self, info, **kwargs):
        """
        gets supplier order name

        Returns:
            string: supplier order name from supplier order details
        """
        return self.get_supplier_order_name

    def resolve_supplier_order_number(self, info, **kwargs):
        """
        gets supplier order number

        Returns:
            string: supplier order number from supplier order details
        """
        return self.get_supplier_order_number

    def resolve_deliver_to(self, info, **kwargs):
        """
        gets outlets a supplier is supposed to deliver the order to

        Returns:
            list: outlets supplier is supposed to deliver to from
                  supplier order details
        """
        return self.deliver_to_outlets

    def resolve_delivery_due(self, info, **kwargs):
        """
        gets the date a supplier is supposed to deliver the order

        Returns:
            date: date when the supplier has to deliver order from
                  supplier order details
        """
        return self.delivery_due_date

    def resolve_payment_due(self, info, **kwargs):
        """
        gets when the payment of the supplier should be paid

        Returns:
            date: when the supplier will be paid from the supplier
                  order details
        """
        return self.payment_due_date


class SupplierOrderDetailsType(DjangoObjectType):
    order_details = graphene.List(ProductBatchType)
    number_of_products = graphene.Int()
    supplier_order_name = graphene.String()
    supplier_order_number = graphene.String()
    deliver_to = graphene.String()
    delivery_due = graphene.Date()
    payment_due = graphene.Date()

    class Meta:
        model = Order

    def resolve_number_of_products(self, info):
        return len(self.order_items())

    def resolve_order_details(self, info, **kwargs):
        """
        get order details

        Returns:
            list: order details of a particular supplier and order
        """
        return self.order_items()

    def resolve_supplier_order_name(self, info, **kwargs):
        """
        gets supplier order name

        Returns:
            string: supplier order name from supplier order details
        """
        return f"{self.order_items()[0].supplier.name}-{self.name}"

    def resolve_supplier_order_number(self, info, **kwargs):
        """
        gets supplier order number

        Returns:
            string: supplier order number from supplier order details
        """
        return self.order_number

    def resolve_deliver_to(self, info, **kwargs):
        """
        gets outlets a supplier is supposed to deliver the order to

        Returns:
            list: outlets supplier is supposed to deliver to from
                  supplier order details
        """
        return self.destination_outlet

    def resolve_delivery_due(self, info, **kwargs):
        """
        gets the date a supplier is supposed to deliver the order

        Returns:
            date: date when the supplier has to deliver order from
                  supplier order details
        """
        return self.delivery_date

    def resolve_payment_due(self, info, **kwargs):
        """
        gets when the payment of the supplier should be paid

        Returns:
            date: when the supplier will be paid from the supplier
                  order details
        """
        return self.delivery_date


class Query(graphene.AbstractType):
    suppliers_order_details = graphene.List(
        SupplierOrderType, order_id=graphene.Int(required=True))
    supplier_order_details = graphene.Field(
        SupplierOrderType, supplier_order_form_id=graphene.String(
            required=True)
    )
    orders = graphene.List(OrderType, page_count=graphene.Int(),
                           page_number=graphene.Int())
    order = graphene.Field(OrderType, order_id=graphene.Int(required=True))
    orders_sorted_by_status = graphene.List(SupplierOrderDetailsType, page_count=graphene.Int(),
                                            page_number=graphene.Int(), status=graphene.String(required=True))
    supplier_orders_sorted_by_status = graphene.List(SupplierOrderType, page_count=graphene.Int(),
                                                     page_number=graphene.Int(), status=graphene.String(required=True))
    closed_orders = graphene.List(OrderType, page_count=graphene.Int(),
                                  page_number=graphene.Int())
    total_orders_pages_count = graphene.Int()
    pagination_result = None
    autosuggest_product_order = graphene.List(AutosuggestOrder)

    supplier_order_form = graphene.Field(
        SupplierOrderType,
        supplier_order_id=graphene.String(required=True)
    )

    all_suppliers_order_forms = graphene.List(SupplierOrderType)

    order_products = graphene.List(OrderProductsType, order_id=graphene.Int())

    all_product_batch = graphene.List(ProductBatchType, page_count=graphene.Int(), page_number=graphene.Int())
    product_batch = graphene.Field(
        ProductBatchType, product_id=graphene.String(),
        order_id=graphene.String(), supplier_id=graphene.String(),
        status=graphene.String()
    )

    @login_required
    def resolve_all_suppliers_order_forms(self, info, **kwargs):
        unique_items = []
        # get all of my orders id's
        orders_id = Order.objects.filter(user_id=info.context.user.id).values_list('id', flat=True)
        # get all the suppliers we have
        suppliers_id = Suppliers.objects.filter(user_id=info.context.user.id).values_list('id', flat=True)

        # for each unique combination we get the corresponsing batches if they exist
        for order_id in orders_id:
            for supplier_id in suppliers_id:
                supplier_order = SupplierOrder.objects.filter(supplier_id=supplier_id, order_id=order_id).first()
                if supplier_order:
                    unique_items.append(supplier_order)

        return unique_items

    @login_required
    def resolve_supplier_order_form(self, info, supplier_order_id):
        supplier_order = SupplierOrder.objects.get(id=supplier_order_id)
        return supplier_order

    @login_required
    def resolve_product_batch(self, info, **kwargs):
        product_id = kwargs.get('product_id')
        order_id = kwargs.get('order_id')
        supplier_id = kwargs.get('supplier_id')
        status = kwargs.get('status')

        if product_id:
            resolved_value = ProductBatch.objects.filter(
                product_id=product_id
            )
            if not resolved_value:
                error = ORDERS_ERROR_RESPONSES['inexistent_batch'].format("product_id", product_id)
                raise GraphQLError(error)
            return resolved_value

        if order_id:
            resolved_value = ProductBatch.objects.filter(
                order_id=order_id
            )
            if not resolved_value:
                error = ORDERS_ERROR_RESPONSES['inexistent_batch'].format("order_id", order_id)
                raise GraphQLError(error)
            return resolved_value

        if supplier_id:
            resolved_value = ProductBatch.objects.filter(
                supplier_id=supplier_id
            )
            if not resolved_value:
                error = ORDERS_ERROR_RESPONSES['inexistent_batch'].format("supplier_id", supplier_id)
                raise GraphQLError(error)
            return resolved_value

        if status:
            resolved_value = ProductBatch.objects.filter(
                status=status
            )
            if not resolved_value:
                error = ORDERS_ERROR_RESPONSES['inexistent_batch'].format("status", status)
                raise GraphQLError(error)
            return resolved_value

        return None

    @login_required
    def resolve_all_product_batch(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')

        allProductBatches = ProductBatch.objects.all()

        if page_count or page_number:
            orders = pagination_query(
                allProductBatches, page_count, page_number)
            Query.pagination_result = orders
            return orders[0]

        paginated_response = pagination_query(allProductBatches,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response

        return paginated_response[0]

    def check_if_orders_are_under_your_business(self, user, orders):
        orders_under_your_business = []
        business = get_user_business(user)

        for order in orders:
            found = Order.objects.filter(id=order['order_id'], business_id=business.id)
            if (found):
                orders_under_your_business.append(order)

        return orders_under_your_business

    def convert_dict_to_object(self, passedDict):
        new_list = []
        for res in passedDict:
            new_list.append(namedtuple(
                'Struct', res.keys())(*res.values()))
        return new_list

    def get_pending_suppliers_order_forms(self, suppliersOrderForms):
        # remove the order which is has a status of ready to be placed because
        # once it has that, it means the real supplier order forms where generated
        # so we use them on it's behalf.
        all_supplier_order_forms = []
        for res in suppliersOrderForms:
            if 'waiting for order to be placed' not in res['status'] \
                    and not res.get('marked_as_sent'):
                all_supplier_order_forms.append(namedtuple(
                    'Struct', res.keys())(*res.values()))

        return all_supplier_order_forms

    def count_repetition_of_object_in_array(self, passedObject):
        # counter how many times it repeats itself in order
        # to get the number of products
        new_counter_object = dict(Counter(passedObject))
        keys = list(new_counter_object.keys())
        values = list(new_counter_object.values())

        # store supplier order form id as a key and
        # value as a number of products
        key_value_object = {}
        for i, res in enumerate(keys):
            key_value_object[list(keys[i])[0]] = values[i]

        return key_value_object

    def remove_duplicates(self, passedObject):
        complete_orders_with_no_duplicates = []
        # remove duplicates
        for res in passedObject:
            if res not in complete_orders_with_no_duplicates:
                complete_orders_with_no_duplicates.append(res)

        return complete_orders_with_no_duplicates

    def get_your_incomplete_orders(self, orders):
        # getting the incomplete order information
        incomplete_orders = []
        for order_detail_item in orders:
            supplier_order_object = {}
            supplier_order_object['order_name'] = order_detail_item.__dict__[
                'name']
            supplier_order_object['order_id'] = order_detail_item.__dict__[
                'id']
            supplier_order_object['order_number'] = order_detail_item.__dict__[
                'order_number']
            supplier_order_object['status'] = order_detail_item.__dict__[
                'status']
            incomplete_orders.append(supplier_order_object)

        return incomplete_orders

    def get_complete_supplier_order_details(
            self, order_details, supplier_order_details):

        complete_orders_with_duplicates = []
        # get the complete order information
        for sod in supplier_order_details:
            for od in order_details:
                if sod.__dict__['order_id'] == od.__dict__['order_id'] \
                        and sod.__dict__['supplier_id'] == od.__dict__['supplier_id']:
                    supplier_order_object = {}
                    supplier_order_object['supplier_order_form_id'] = sod.__dict__[
                        'id']
                    supplier_order_object['order_id'] = od.__dict__['order_id']
                    supplier_order_object['supplier_id'] = od.__dict__[
                        'supplier_id']
                    supplier_order_object['status'] = "Awaiting order send-out..."
                    supplier_order_object['supplier_order_name'] = od.__dict__[
                        'supplier_order_name']
                    supplier_order_object['supplier_order_number'] = od.__dict__[
                        'supplier_order_number']
                    supplier_order_object['marked_as_sent'] = sod.__dict__[
                        'marked_as_sent']
                    complete_orders_with_duplicates.append(
                        supplier_order_object)

        return complete_orders_with_duplicates

    @login_required
    def resolve_suppliers_order_details(self, info, **kwargs):
        """
        gets order details for suppliers of that order

        Returns:
            list: supplier order details of a particular order
        """
        order = get_model_object(Order, 'id', kwargs.get('order_id'))
        return SupplierOrder.objects.filter(order=order)

    @login_required
    def resolve_supplier_order_details(self, info, **kwargs):
        supplier_order_details = SupplierOrder.objects.filter(
            id=kwargs['supplier_order_form_id']).first()

        business = get_user_business(info.context.user)
        orders = Order.objects.filter(
            user_id=info.context.user.id,
            business=business
        ).order_by('id')

        order_ids = []
        for order in orders:
            order_ids.append(order.id)
        # check if the supplier order exists in the first place
        if not supplier_order_details:
            raise ValueError('The supplier order form id does not exist')
        # check if supplier order details is under your orders
        if supplier_order_details.order_id not in order_ids:
            raise ValueError('The supplier order form id is not under your business')

        return supplier_order_details

    @login_required
    def resolve_orders(self, info, **kwargs):
        """
        gets all orders

        Returns:
            list: orders
        """
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        business = get_user_business(info.context.user)
        # get the first outlet of the user
        user_outlet = OutletUser.objects.filter(
            user_id=info.context.user.id
        ).first()
        orders_set = Order.objects.filter(
            outlet=user_outlet.outlet,
            business=business
        ).order_by('id')
        if page_count or page_number:
            orders = pagination_query(
                orders_set, page_count, page_number)
            Query.pagination_result = orders
            return orders[0]
        paginated_response = pagination_query(orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_total_orders_pages_count(self, info, **kwargs):
        """
        :param info:
        :param kwargs:
        :return: Total number of pages for a specific pagination response
        :Note: During querying, totalOrdersPagesCount query field should
        strictly be called after the orders query when the pagination
        is being applied, this is due to GraphQL order of resolver methods
        execution.
        """
        if not Query.pagination_result:
            return 0
        return Query.pagination_result[1]

    @login_required
    def resolve_order(self, info, **kwargs):
        """
        gets a single order

        Returns:
            obj: an order
        """
        return get_model_object(Order, 'id', kwargs.get('order_id'))

    @login_required
    def resolve_orders_sorted_by_status(self, info, **kwargs):
        """
        gets orders that are based on their status

        Returns:
            list: orders
        """
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        status = kwargs.get('status')
        business = get_user_business(info.context.user)
        # get the first outlet of the user
        user_outlet = OutletUser.objects.filter(
            user_id=info.context.user.id,
        ).first()
        orders_set = Order.objects.filter(
            status=status,
            outlet=user_outlet.outlet,
            business=business
        ).order_by('id')

        if page_count or page_number:
            orders_sorted_by_status = pagination_query(
                orders_set, page_count, page_number)
            Query.pagination_result = orders_sorted_by_status
            return orders_sorted_by_status[0]
        paginated_response = pagination_query(orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_supplier_orders_sorted_by_status(self, info, **kwargs):
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        status = kwargs.get('status')
        business = get_user_business(info.context.user)
        # get the first outlet of the user
        user_outlet = OutletUser.objects.filter(
            user_id=info.context.user.id,
        ).first()
        orders_set = Order.objects.filter(
            # status=status,
            outlet=user_outlet.outlet,
            business=business
        ).order_by('id')
        supplier_order_forms = []
        for order in orders_set:
            for supplier_order_form in order.get_supplier_order_forms(status):
                supplier_order_forms.append(supplier_order_form)
        if page_count or page_number:
            supplier_orders_sorted_by_status = pagination_query(
                supplier_order_forms, page_count, page_number)
            Query.pagination_result = supplier_orders_sorted_by_status
            return supplier_orders_sorted_by_status[0]
        paginated_response = pagination_query(orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_closed_orders(self, info, **kwargs):
        """
        gets orders that have been closed

        Returns:
            list: closed orders
        """
        page_count = kwargs.get('page_count')
        page_number = kwargs.get('page_number')
        business = get_user_business(info.context.user)
        # get the first outlet of the user
        user_outlet = OutletUser.objects.filter(
            user_id=info.context.user.id,
        ).first()

        closed_orders_set = Order.objects.filter(
            closed=True,
            outlet=user_outlet.outlet,
            business=business
        ).order_by('id')
        if page_count or page_number:
            closed_orders = pagination_query(
                closed_orders_set, page_count, page_number)
            Query.pagination_result = closed_orders
            return closed_orders[0]
        paginated_response = pagination_query(closed_orders_set,
                                              PAGINATION_DEFAULT[
                                                  "page_count"],
                                              PAGINATION_DEFAULT[
                                                  "page_number"])
        Query.pagination_result = paginated_response
        return paginated_response[0]

    @login_required
    def resolve_autosuggest_product_order(self, info, **kwargs):
        """
        Auto suggest products that needs to be ordered and the
        quantity that needs to be ordered for based on the sales
        velocity calculator

        Returns:
            list: tuple(product_name, quantity)
        """
        user = info.context.user
        outlet = check_user_has_an_active_outlet(user)
        product_to_order = autosuggest_product_order(outlet=outlet)
        return product_to_order

    @login_required
    def resolve_order_products(self, info, **kwargs):
        """
        Auto suggest products that needs to be ordered and the
        quantity that needs to be ordered for based on the sales
        velocity calculator

        Returns:
            list: tuple(product_name, quantity)
        """

        order_id = kwargs.get('order_id')
        orders_products = OrdersProducts.objects.filter(
            order_id=order_id, is_deleted=False
        ).order_by('-created_at')
        return orders_products
