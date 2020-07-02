"""Service objects that implement business logic."""
from graphql.error import GraphQLError

from healthid.apps.orders.models import \
    Order, SupplierOrderDetails, SuppliersContacts, Suppliers
from healthid.utils.app_utils.send_mail import SendMail
from healthid.apps.orders.models.orders import OrdersProducts
from healthid.apps.orders.models.orders import ProductBatch, SupplierOrder
from healthid.utils.app_utils.database import (get_model_object,
                                               SaveContextManager)
from healthid.apps.outlets.models import Outlet
from healthid.utils.messages.orders_responses import (
    ORDERS_SUCCESS_RESPONSES, ORDERS_ERROR_RESPONSES)


class SupplierOrderDetailsFetcher:
    """Defines an object that fetches supplier order details

    Args:
        order_id(String): The id of an order
        supplier_order_details_ids (List): a list of supplier order ids
    """

    def __init__(self, supplier_order_details_ids):
        self.supplier_order_details_ids = supplier_order_details_ids

    def fetch(self):
        """Get Supplier Order Details

        Get all supplier order details belong to provided order and match
        the provided ids.

        Returns:
            (Obj:) QuerySet object of supplier order details
        """
        results = SupplierOrderDetails.objects.all()
        results = results.filter(
            id__in=self.supplier_order_details_ids)
        if not results:
            raise ValueError("No supplier Order Details found matching "
                             "provided ids and Order")
        return results


class SupplierOrderEmailSender:
    """Defines an object that sends order emails to suppliers.

    Args:
        supplier_order_ids: A list of supplier ids and  order ids 
        e.g [{
                supplierId:supplierId(String)
                orderId:orderId(Int)
            }]
    """

    def __init__(self, supplier_order_ids):
        self.supplier_order_ids = supplier_order_ids

    def send(self):

        for supplier_order_id in self.supplier_order_ids:
            supplier_order = SupplierOrder.objects.get(id=supplier_order_id)
            supplier_id = supplier_order.supplier.id
            order_id = supplier_order.order.id

            if not (supplier_id and order_id):
                continue
            default_supplier = supplier_order.supplier
            order =  supplier_order.order
            supplier_contacts_items = default_supplier.get_supplier_contacts
            outlet = Outlet.objects.get(id=order.destination_outlet_id)
            supplier_contacts = [
                contact for contact in supplier_contacts_items if contact['outlet_id'] == order.destination_outlet_id
            ]
            email = supplier_contacts[0]["email"] if len(supplier_contacts) else None
            if email is None or (isinstance(email, str) and '@' not in email):
                email = outlet.outlet_manager.email
            emailDetails = {}
            emailDetails['supplier_order'] = supplier_order
            emailDetails['supplier_id'] = supplier_order.supplier_id
            emailDetails['order_id'] = supplier_order.order_id
            emailDetails['order_details'] = supplier_order.get_product_batches()
            emailDetails['outlet'] = outlet
            emailDetails['outlet_contacts'] = outlet.get_outlet_contacts
            emailDetails['delivery_due'] = order.delivery_date.strftime('%d/%m/%Y')
            emailDetails['payment_due'] = order.delivery_date.strftime('%d/%m/%Y')
            payment_days = order.delivery_date - order.delivery_date
            if payment_days:
                emailDetails['payment_term'] = f"{payment_days.days} days credit"
            else:
                emailDetails['payment_term'] = "Cash On Delivery"
            emailDetails['supplier_order_name'] = default_supplier.name
            emailDetails['supplier_order_number'] = order.id
            self._send_single_email(email, emailDetails)
            order.sent_status = True
            order.save()

        return ORDERS_SUCCESS_RESPONSES["supplier_order_email_success"].format('')

    @staticmethod
    def _send_single_email(email, detail):
        context = {'detail': detail}
        mail = SendMail(
            to_email=[email],
            subject='Supplier Order Form Email',
            template='email_alerts/orders/supplier_order_email.html',
            context=context
        )
        mail.send()


class SupplierOrderDetailsApprovalService:
    """A service object that approves supplier order details.

    Approve a supplier order detail indicating the approver.
    Change the status of the supplier order detail to "Open"

    Args:
        supplier_order_detail: a supplier order details object
        user: a User object

    Returns:
        (Obj:) supplier_order_detail
    """

    def __init__(self, supplier_orders, user, additional_notes=None):
        self.supplier_orders = supplier_orders
        self.user = user
        self.additional_notes = additional_notes

    def approve(self):
        """Approve multiple supplier order details.

        Returns:
            message: A return message
        """
        no_of_orders = len(self.supplier_orders)

        ids = list()
        for supplier_order in self.supplier_orders:
            self._approve_single_detail(supplier_order, self.user)
            if no_of_orders == 1:
                supplier_order.additional_notes = self.additional_notes

            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                ids.append(supplier_order.id)

        return ORDERS_SUCCESS_RESPONSES[
            "supplier_order_approval_success"].format(
                ', '.join([id for id in ids]))

    @staticmethod
    def _approve_single_detail(supplier_order, user):
        """Approve single a supplier order.

        Returns:
            (Obj): SupplierOrderDetails instance
        """
        supplier_order.approved_by = user
        supplier_order.approved = True
        return supplier_order


class SupplierOrderStatusChangeService:
    """A service object that chnages supplier order details
    status to approved.

    Approve a supplier order detail indicating the approver.
    Change the status of the supplier order detail to "Approved"

    Args:
        supplier_order_detail: a supplier order id

    Returns:
        (Obj:) supplier_order_detail
    """

    def __init__(self, supplier_order_details_id, user):
        self.user = user
        self.supplier_order_details_id = supplier_order_details_id

    def change_status(self):
        if self.supplier_order_details_id[0] == "":
            raise GraphQLError(ORDERS_ERROR_RESPONSES[
                'none_supplier_order_id'])
        results = SupplierOrderDetails.objects.all()
        supplier_order = results.filter(
            id__in=self.supplier_order_details_id).first()
        if supplier_order:
            if supplier_order.approved is not True:
                raise GraphQLError(ORDERS_ERROR_RESPONSES[
                    'supplier_order_not_approved'].format('approved'))
            supplier_order.status = 'approved'
            supplier_order.approved_by = self.user
            with SaveContextManager(supplier_order,
                                    model=SupplierOrderDetails):
                return ORDERS_SUCCESS_RESPONSES[
                    "supplier_order_mark_status"
                ].format(self.supplier_order_details_id)
        raise GraphQLError(ORDERS_ERROR_RESPONSES[
            'no_supplier_order_id'].format(self.supplier_order_details_id))


class OrderStatusChangeService:
    """A service object that changes order status

    - once an order has been initiated, system should give the order a status of
        `Incomplete order form`
    - when order list has been populated and generated, the system should give the
        supplier order a status of `waiting for order to be placed`
    - when the order has been placed and auto-sent to the supplier, the system should
        give the supplier order a status of `Open`
    - when all ordered products have been assigned batches and the user has closed the
        order, system should give the supplier order a status of `Closed`

    Args:
        order_id: an order id
        status: new status of the order

    Returns:
        (Obj:) updated_order
    """

    def __init__(self, order_id, status):
        self.order_id = order_id
        self.status = status

    def change_status(self):
        update_order_status = Order.objects.filter(
            id=self.order_id).first()
        update_order_status.status = self.status
        update_order_status.save()


class SaveAutofillItems:
    def __init__(self, product_list, order_id):
        self.product_list = product_list
        self.order_id = order_id

    def save(self):
        if self.product_list:
            order_exists = OrdersProducts.objects.filter(
                order_id=self.order_id)
            if not order_exists:
                for product in self.product_list:
                    OrdersProducts.objects.get_or_create(
                        order_id=self.order_id,
                        product_unit_price=product.sales_price,
                        product_name=product.product_name,
                        product_id=product.id,
                        sku_number=product.sku_number,
                        current_supplier_id=product.preferred_supplier_id,
                        product_quantity=product.autofill_quantity,
                        preferred_supplier_id=product.preferred_supplier_id,
                        backup_supplier_id=product.backup_supplier_id,
                    )
            return OrdersProducts.objects.filter(
                is_deleted=False, order_id=self.order_id)
        return None
