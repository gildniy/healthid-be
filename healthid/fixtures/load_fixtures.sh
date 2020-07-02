#!/bin/bash

# the script to create data in the database
# they are arranged according to dependency of models

python manage.py loaddata healthid/fixtures/role_data.json &&
    python manage.py loaddata healthid/fixtures/authentication.json &&
    python manage.py loaddata healthid/fixtures/business.json &&
    python manage.py loaddata healthid/fixtures/countries.json &&
    python manage.py loaddata healthid/fixtures/event_types.json &&
    python manage.py loaddata healthid/fixtures/dispensing_size.json &&
    python manage.py loaddata healthid/fixtures/outlets.json &&
    python manage.py loaddata healthid/fixtures/product_category.json &&
    python manage.py loaddata healthid/fixtures/tiers.json &&
    python manage.py loaddata healthid/fixtures/timezones.json &&
    python manage.py loaddata healthid/fixtures/orders.json &&
    python manage.py loaddata healthid/fixtures/orders_products.json &&
    python manage.py loaddata healthid/fixtures/products.json &&
    python manage.py loaddata healthid/fixtures/stocks.json &&
    python manage.py loaddata healthid/fixtures/stock_count.json &&
    python manage.py loaddata healthid/fixtures/sales.json &&
    python manage.py loaddata healthid/fixtures/sales_return.json &&
    python manage.py loaddata healthid/fixtures/consultation_data.json
