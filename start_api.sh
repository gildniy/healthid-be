#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8


echo "<<<<<<<< Database Setup and Migrations Starts >>>>>>>>>"

# Run database migrations
python3 manage.py makemigrations && python3 manage.py migrate

# the script to create data in the database
# they are arranged according to dependency of models
# python manage.py loaddata healthid/fixtures/role_data.json &&
# python manage.py loaddata healthid/fixtures/authentication.json &&
# python manage.py loaddata healthid/fixtures/business.json &&
# python manage.py loaddata healthid/fixtures/countries.json &&
# python manage.py loaddata healthid/fixtures/event_types.json &&
# python manage.py loaddata healthid/fixtures/dispensing_size.json &&
# python manage.py loaddata healthid/fixtures/outlets.json &&
# python manage.py loaddata healthid/fixtures/product_category.json &&
# python manage.py loaddata healthid/fixtures/promotion.json &&
# python manage.py loaddata healthid/fixtures/tiers.json &&
# python manage.py loaddata healthid/fixtures/timezones.json &&
# python manage.py loaddata healthid/fixtures/orders.json &&
# python manage.py loaddata healthid/fixtures/orders_products.json &&
# python manage.py loaddata healthid/fixtures/outlet.json &&
# python manage.py loaddata healthid/fixtures/products.json &&
# python manage.py loaddata healthid/fixtures/stocks.json &&
# python manage.py loaddata healthid/fixtures/stock_count.json &&
# python manage.py loaddata healthid/fixtures/sales.json &&
# python manage.py loaddata healthid/fixtures/sales_return.json &&
# python manage.py loaddata healthid/fixtures/consultation_data.json



echo "<<<<<<<<<<<<<<<<<<<< START API >>>>>>>>>>>>>>>>>>>>>>>>"
sleep 3

# Start the API
gunicorn --workers 2 -t 3600 healthid.wsgi -b 0.0.0.0:80 --access-logfile '-' --reload
