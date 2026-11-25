#!/usr/bin/env bash
# Render build script: exit on the first error.
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input

# Optional: create the admin account on the first deploy (Render's free plan
# has no shell). Set DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_EMAIL and
# DJANGO_SUPERUSER_PASSWORD in Render, deploy once, then delete the password.
if [[ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]]; then
    python manage.py createsuperuser --no-input || true
fi
