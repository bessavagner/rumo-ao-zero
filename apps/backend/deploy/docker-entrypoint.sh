#!/bin/sh
set -e

# Garante o schema no SQLite do volume montado ($DB_PATH).
python manage.py migrate --noinput

# Cloud Run define $PORT (default 8080); bind em 0.0.0.0.
# Com SQLite, mantenha WEB_CONCURRENCY=1 e max-instances=1 (ver deploy/README.md).
exec gunicorn config.wsgi:application \
    --bind "0.0.0.0:${PORT:-8080}" \
    --workers "${WEB_CONCURRENCY:-2}" \
    --timeout 60
