#!/bin/sh

# Exit upon command exiting with non-zero status
set -e

# Perform migrations before turning on prod server
python manage.py migrate

# Run custom management command to seed db before turning on prod server
python manage.py seed_data

# Start the Gunicorn server
gunicorn wrs_api.wsgi --bind 0.0.0.0:8000