#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
python manage.py make
# the script to create data in the database
# they are arranged according to dependency of models
python3 manage.py loaddata healthid/fixtures/authentication.json && 
python3 manage.py loaddata healthid/fixtures/business.json && 
python3 manage.py loaddata healthid/fixtures/consultation_data.json &&
python3 manage.py loaddata healthid/fixtures/countries.json && 
python3 manage.py loaddata healthid/fixtures/event_types.json && 
python3 manage.py loaddata healthid/fixtures/measurement_unit.json && 
python3 manage.py loaddata healthid/fixtures/outlets.json && 
python3 manage.py loaddata healthid/fixtures/product_category.json && 
python3 manage.py loaddata healthid/fixtures/promotion.json && 
python3 manage.py loaddata healthid/fixtures/role_data.json && 
python3 manage.py loaddata healthid/fixtures/tiers.json && 
python3 manage.py loaddata healthid/fixtures/timezones.json && 
python3 manage.py loaddata healthid/fixtures/orders.json && 
python3 manage.py loaddata healthid/fixtures/orders_products.json && 
python3 manage.py loaddata healthid/fixtures/outlet.json && 
python3 manage.py loaddata healthid/fixtures/products.json && 
python3 manage.py loaddata healthid/fixtures/stocks.json && 
python3 manage.py loaddata healthid/fixtures/stock_count.json
