from datetime import timedelta
from decimal import Decimal
from django.db import models
from django.conf import settings

from healthid.apps.orders.models.suppliers import Suppliers, SuppliersMeta
from healthid.apps.outlets.models import Outlet
from healthid.apps.products.models import Product
from healthid.models import BaseModel
from healthid.utils.messages.orders_responses import ORDERS_ERROR_RESPONSES, \
    ORDERS_SUCCESS_RESPONSES
from healthid.utils.app_utils.id_generator import id_gen
from healthid.utils.app_utils.database import get_model_object
from healthid.apps.authentication.models import User
from healthid.apps.business.models import Business


class Order(BaseModel):
    """
        Class to handle order data
    """
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(
        max_length=9, default=id_gen, editable=False
    )
    name = models.TextField(null=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True,
        related_name='created_orders')
    business = models.ForeignKey(
        Business, on_delete=models.CASCADE, null=True)
    outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        default=1,
        related_name='user_outlet'
    )
    product_autofill = models.BooleanField(default=True)
    supplier_autofill = models.BooleanField(default=True)
    destination_outlet = models.ForeignKey(
        Outlet,
        on_delete=models.CASCADE,
        default=1,
    )
    delivery_date = models.DateField()
    status = models.CharField(
        default="Incomplete order form", null=True, max_length=50)
    sent_status = models.BooleanField(default=False)
    closed = models.BooleanField(default=False)

    def get_supplier_order_forms(self, status='PENDING_DELIVERY'):
        if status == 'ALL':
            return SupplierOrder.objects.filter(order_id=self.id)
        return SupplierOrder.objects.filter(order_id=self.id, status=status)

    def order_items(self):
        order_items_list = ProductBatch.objects.filter(
            order_id = self.id
        )
        return order_items_list

    def close(self, user):
        """
        Close an open order

        Arguments:
            user(object): User initiating the close request

        Returns:
            str: response message
        """

        if self.destination_outlet.id != user.active_outlet.id:
            raise ValueError(
                ORDERS_ERROR_RESPONSES[
                    'close_order_invalid_user'])
        if self.closed:
            return ORDERS_SUCCESS_RESPONSES[
                'already_closed_order'].format(self.order_number)
        else:
            self.closed = True
            self.save()
            return ORDERS_SUCCESS_RESPONSES[
                'order_close_success'].format(self.order_number)


class OrderDetails(BaseModel):
    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    ordered_quantity = models.IntegerField()
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE,
                                 null=True)
    cost_per_item = models.CharField(
        max_length=50, null=True, editable=True
    )
    price = models.CharField(max_length=50, null=True, editable=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    supplier_order_name = models.CharField(
        max_length=100, null=True, editable=False
    )
    supplier_order_number = models.CharField(
        max_length=50, null=True, editable=False
    )
    @classmethod
    def check_if_duplicate(self, order_id, order_detail_object, supplier=None):
        """
        Adds a supplier value to the 'OrderDetail' object
        Checks for duplicate order details records in the database
        If not duplicated, bulk creates new 'OrderDetail' records

        Arguments:
            order_id(int): Id of the 'Order' that the
                          'OrderDetail' object is for
            order_detail_object(list): list of 'OrderDetail' model objects
                                       to be saved
            supplier(iter): iterable of suppliers whose order details are
                      being created

        Returns:
            created_order(obj): latest order detail created
        """
        detail_object_list = []
        for detail_object in order_detail_object:
            if supplier is None:
                product = get_model_object(
                    Product,
                    'id',
                    detail_object.product_id
                )
                supplier_id = product.preferred_supplier.id
            else:
                supplier_id = next(supplier)
            check_duplicate = self.objects.filter(
                order__id=order_id,
                product__id=detail_object.product_id,
                supplier__id=supplier_id
            ).exists()
            if not check_duplicate:
                detail_object.supplier_id = supplier_id
                detail_object.supplier_order_number = \
                    str(detail_object.order.order_number) + '-' + supplier_id
                detail_object.supplier_order_name = \
                    detail_object.supplier.name + '-' + detail_object.order.name
                detail_object_list.append(detail_object)
                created_order = detail_object
            else:
                current_order_detail = OrderDetails.objects.get(
                    order__id=order_id,
                    product__id=detail_object.product_id,
                    supplier__id=supplier_id
                )
                current_order_detail.ordered_quantity = \
                    detail_object.ordered_quantity
                current_order_detail.price = detail_object.price
                current_order_detail.cost_per_item = \
                    detail_object.cost_per_item
                current_order_detail.save()
                created_order = current_order_detail

        OrderDetails.objects.bulk_create(detail_object_list)
        return created_order

    @property
    def get_order_form(self):
        supplier_order_form = SupplierOrderDetails.objects.filter(
            order=self.order, supplier=self.supplier)
        return supplier_order_form[0]


class SupplierOrderDetails(BaseModel):
    """
    defines supplier order details model

    Args:
        grand_total: possible price of the order for supplier
        additional_notes: notes about the order from a supplier
        order: order the order details of a supplier belong to
        supplier: supplier of order details
    """
    PENDING = "pending"
    OPEN = "open"
    CLOSED = "closed"
    APPROVED = "approved"

    ORDER_STATUSES = (
        (PENDING, "Pending Approval"),
        (OPEN, "Open"),
        (CLOSED, "Closed"),
        (APPROVED, "Approved")
    )

    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False
    )
    grand_total = models.DecimalField(blank=True, null=True,
                                      max_digits=10, decimal_places=2)
    additional_notes = models.CharField(max_length=500, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                    related_name="approved_supplier_orders",
                                    on_delete=models.CASCADE)
    marked_as_sent = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=ORDER_STATUSES,
                              default=PENDING)

    @property
    def get_order_details(self):
        """
        get order details of a supplier based on order

        Returns:
            list: order details of a single supplier from an order
        """
        return self.order.orderdetails_set.all().filter(supplier=self.supplier)

    @property
    def get_supplier_order_name(self):
        """
        generates order name for a supplier

        Returns:
            string: combination of order name and supplier order details
                    id
        """
        return self.supplier.name + '-' + self.order.name

    @property
    def get_supplier_order_number(self):
        """
        generates order number for a supplier

        Returns:
            string: combination of order number and supplier order
                    details id
        """
        return self.order.order_number + '-' + self.supplier.supplier_id

    @property
    def deliver_to_outlets(self):
        """
        gets the outlets a supplier will deliver to

        Returns:
            list: outlets a supplier will deliver to
        """
        return self.order.destination_outlet

    @property
    def delivery_due_date(self):
        """
        gets the date the order should be delivered by

        Returns:
            date: when the supplier has to deliver the order
        """
        return self.order.delivery_date

    @property
    def payment_due_date(self):
        """
        determines when the supplier should be paid

        Returns:
            date: when the supplier expects to be paid for thr order
        """
        supplier_meta = SuppliersMeta.objects.all().filter(
            supplier=(self.supplier)).first()
        return self.delivery_due_date + timedelta(
            days=supplier_meta.credit_days if supplier_meta else 0)

    @property
    def order_status(self):
        """Returns the status of the supplier order form.

        Returns:
            status: displayable version of the status.
        """
        return self.get_status_display()


class OrdersProducts(BaseModel):
    """
    Class to handle autoFill products suggested
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    product_name = models.CharField(null=True, max_length=100)
    product_unit_price = models.IntegerField(null=True, blank=True)
    sku_number = models.IntegerField(null=True)
    product = models.ForeignKey(
        Product,
        related_name='product',
        on_delete=models.CASCADE,
        null=True, blank=True)
    product_quantity = models.IntegerField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    current_supplier = models.ForeignKey(
        Suppliers,
        related_name='current',
        on_delete=models.CASCADE,
        null=True, blank=True)
    preferred_supplier = models.ForeignKey(
        Suppliers,
        related_name='primary',
        on_delete=models.CASCADE,
        null=True, blank=True)
    backup_supplier = models.ForeignKey(
        Suppliers,
        related_name='secondary',
        on_delete=models.CASCADE,
        null=True, blank=True)

    class Meta:
        unique_together = (("product_name", "sku_number",
                            "product_quantity", "order"))

    def __str__(self):
        return self.product_name

class ProductBatch(BaseModel):
    """
    A class to hold a batch of products
    """
    PENDING_ORDER = "PENDING_ORDER"
    PENDING_DELIVERY = "PENDING_DELIVERY"
    CANCELLED = "CANCELLED"
    NOT_RECEIVED = "NOT_RECEIVED"
    NOT_ACCEPTED = "NOT_ACCEPTED"
    RETURNED = "RETURNED"
    IN_STOCK = "IN_STOCK"
    OUT_OF_STOCK = "OUT_OF_STOCK"
    EXPIRED = "EXPIRED"

    ORDER_STATUSES = (
        (PENDING_ORDER, "A order which is pending"),
        (PENDING_DELIVERY, "A delivery yet to be made"),
        (NOT_ACCEPTED, "An order which has been cancelled"),
        (NOT_RECEIVED, "An order which is yet to be recieved"),
        (NOT_ACCEPTED, "An order which has yet to be accepted"),
        (RETURNED, "An order which is returned"),
        (IN_STOCK, "Still in stock"),
        (OUT_OF_STOCK, "Out of stock"),
        (EXPIRED, "Expired Products")
    )

    id = models.CharField(
        max_length=9, primary_key=True, default=id_gen, editable=False)
    outlet = models.ForeignKey(Outlet, on_delete=models.PROTECT, null=True)
    business = models.ForeignKey(Business, on_delete=models.PROTECT, null=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE, null=True)
    product =  models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    batch_ref = models.CharField(max_length=100, null=True)
    date_received = models.DateField(auto_now=False, null=True)
    expiry_date = models.DateField(auto_now=False, null=True)
    quantity = models.PositiveIntegerField(null=True)
    status = models.CharField(max_length=25, choices=ORDER_STATUSES,
                              default=PENDING_ORDER,null=True)
    unit_cost = models.DecimalField(
        max_digits=20, decimal_places=2, default=Decimal('0.00'))

    @property
    def get_backup_supplier(self):
        if self.product.backup_supplier_id:
            return Suppliers.objects.get( id = self.product.backup_supplier_id )

    @property
    def get_preferred_supplier(self):
        if self.product.preferred_supplier_id:
            return Suppliers.objects.get( id = self.product.preferred_supplier_id ) 


class SupplierOrder(BaseModel):
    """
    defines a model for the supplier order 
    Args:
        grand_total : possible price of the order for supplier
        order :  The information about the order
        supplier : The information about the supplier
    """

    STARTED = "STARTED"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    CANCELLED = "CANCELLED"
    APPROVED = "APPROVED"
    PENDING_DELIVERY = "PENDING_DELIVERY"
    RECEIVED = "RECEIVED"
    CLOSED = "CLOSED"

    SUPPLIER_ORDER_STATUSES = (
        (STARTED, "A supplier order which has been started"),
        (PENDING_APPROVAL, "A delivery yet to be made"),
        (CANCELLED, "An order which has been cancelled"),
        (APPROVED, "An order which is yet to be recieved"),
        (PENDING_DELIVERY, "An order which has yet to be accepted"),
        (RECEIVED, "An order which is returned"),
        (CLOSED, "Still in stock"),
    )

    id = models.CharField(
            max_length=9, primary_key=True, default=id_gen, editable=False
        )
    grand_total = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
        )
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Suppliers, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20, choices=SUPPLIER_ORDER_STATUSES, default=STARTED
        )
    additional_notes = models.CharField(max_length=500, blank=True, null=True)
    service_quality = models.PositiveIntegerField(default=3)
    delivery_promptness = models.BooleanField(default=True)

    class Meta:
        unique_together = (("order", "supplier"))
        
    
    def get_product_batches(self):
        """
        gets a list of the product batches corresponding to the supplier and order

        Returns:
            list: a list of corresponding product batches
        """
        product_batches_list = ProductBatch.objects.filter(
            order_id = self.order_id,
            supplier_id = self.supplier_id
        )
        return product_batches_list

    @property
    def get_supplier_order_name(self):
        """
        generates order name for a supplier

        Returns:
            string: combination of order name and supplier order details
                    id
        """ 
        return self.supplier.name + '-' + self.order.name

    @property
    def get_supplier_order_number(self):
        """
        generates order number for a supplier

        Returns:
            string: combination of order number and supplier order
                    details id
        """
        return self.order.order_number + '-' + self.supplier.supplier_id

    @property
    def deliver_to_outlets(self):
        """
        gets the outlets a supplier will deliver to

        Returns:
            list: outlets a supplier will deliver to
        """
        return self.order.destination_outlet

    @property
    def delivery_due_date(self):
        """
        gets the date the order should be delivered by

        Returns:
            date: when the supplier has to deliver the order
        """
        return self.order.delivery_date

    @property
    def payment_due_date(self):
        """
        determines when the supplier should be paid

        Returns:
            date: when the supplier expects to be paid for the order
        """
        supplier_meta = SuppliersMeta.objects.all().filter(
            supplier=(self.supplier)).first()
        return self.delivery_due_date + timedelta(
            days=supplier_meta.credit_days if supplier_meta else 0)
