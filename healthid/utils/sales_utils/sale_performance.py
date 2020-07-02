from healthid.apps.sales.models import SalesPerformance, Sale, SaleDetail

def populate_sale_performace_table():
    """
    populate the sale performance table with data from sale details and sale table
    """
    # firstly get all the sale_id of the most recent sales performance

    most_recent_sale_performance = SalesPerformance.objects.all().order_by("sale_id").last()
    
    if most_recent_sale_performance:
        total_sale_details = SaleDetail.objects.filter(sale_id__gt = most_recent_sale_performance.sale_id)
    else:
        total_sale_details = SaleDetail.objects.all()

    # add all not present in the db
    for existing_sale_detail in total_sale_details:
        corresponding_sale = Sale.objects.get(id = existing_sale_detail.sale_id)
        new_sale_performance = SalesPerformance()

        new_sale_performance.product_id = existing_sale_detail.product_id
        new_sale_performance.unit_price = existing_sale_detail.price
        new_sale_performance.discount = existing_sale_detail.discount
        new_sale_performance.quantity_sold = existing_sale_detail.quantity

        new_sale_performance.sale_id = corresponding_sale.id
        new_sale_performance.cashier_id = corresponding_sale.sales_person_id
        new_sale_performance.outlet_id = corresponding_sale.outlet_id
        new_sale_performance.customer_id = corresponding_sale.customer_id
        new_sale_performance.subtotal = corresponding_sale.sub_total
        new_sale_performance.transaction_date = corresponding_sale.created_at

        new_sale_performance.save()
