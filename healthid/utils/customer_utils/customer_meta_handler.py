from healthid.apps.customers.models import CustomerMeta

customer_meta_object = {
    "last_sale_dt": "",
    "lty_lvl": "",
    "lty_opt_in": "",
    "lty_enroll_date": "",
    "prc_lvl": "",
    "str_credit": "",
    "title": "",
    "customer_type": "",
    "disc": "",
    "last_sale": ""
}


def add_customer_metadata(customer, items):
    for (key, value) in items.items():
        if key in customer_meta_object and value:
            if value:
                CustomerMeta.objects.create(
                    customer=customer, dataKey=key, dataValue=value
                )
