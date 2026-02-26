#!/usr/bin/env bash
set -o errexit

# Install dependencies, collect static files, migrate database
pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate

# Create superuser automatically using environment variables
# Make sure these variables are set in Render Environment Variables:
#   SUPERUSER_NAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD
python manage.py createsuperuser \
    --no-input \
    --username "$SUPERUSER_NAME" \
    --email "$SUPERUSER_EMAIL" \
    || echo "Superuser already exists, skipping..."