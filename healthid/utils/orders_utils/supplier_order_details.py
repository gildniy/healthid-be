from itertools import groupby
from healthid.apps.orders.models.orders import SupplierOrderDetails
from healthid.utils.app_utils.database import SaveContextManager


def create_suppliers_order_details(order, supplier=None):
    """
    function to generate supplier order details for an order

    Args:
        order(obj): order whose supplier order details are to be
                    generated

    Returns:
        list: suppliers order details of a particular order
    """
    order_details = order.orderdetails_set.all().order_by('supplier')
    order_details_by_suppliers = [list(result) for key, result in groupby(
        order_details, key=lambda order_detail: order_detail.supplier)]
    suppliers_order_details = []
    for order_details_per_supplier in order_details_by_suppliers:
        supplier_name = order_details_per_supplier[0].supplier
        check_duplicate = SupplierOrderDetails.objects.filter(
            order=order,
            supplier=supplier_name
        ).exists()
        supplier_order_details = SupplierOrderDetails(
            order=order,
            supplier=order_details_per_supplier[0].supplier)

        grand_total = 0

        # calculate the grand total of products of a given supplier
        for order_detail in order_details:
            if order_details_per_supplier[0].supplier_id ==\
                    order_detail.supplier_id:
                grand_total += int(order_detail.price)

        # set the grand total
        supplier_order_details.grand_total = grand_total

        if not check_duplicate:
            with SaveContextManager(
                supplier_order_details, model=SupplierOrderDetails
            ) as supplier_order_details:
                suppliers_order_details.append(supplier_order_details)
        else:
            current_supplier_detail = SupplierOrderDetails.objects.get(
                order=order,
                supplier=supplier_name
            )

            # if the price is updated then update the grand total amount
            if (current_supplier_detail.grand_total != grand_total):
                obj = SupplierOrderDetails.objects.get(
                    supplier_id=current_supplier_detail.supplier_id)
                obj.grand_total = grand_total
                obj.save()

            suppliers_order_details.append(current_supplier_detail)
    return suppliers_order_details
