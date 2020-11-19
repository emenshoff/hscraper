#!/bin/sh

set -e

python manage.py collect static --noinput

uwsgi --socket :8000 --master --enable-threads --module app.wsgi

