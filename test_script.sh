#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8

echo "<<<<<<<<<<<<<<<<<<<< RUN Test >>>>>>>>>>>>>>>>>>>>>>>>"

# Start the API
# python manage.py test /src/healthid/tests/authentication/test_add_user.py
cd /src
virtualenv ../venv/.
source ../venv/bin/activate
gunicorn --workers 2 -t 3600 healthid.wsgi -b 0.0.0.0:8000 --access-logfile '-' --reload



