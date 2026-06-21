#!/usr/bin/env bash
set -euo pipefail

pip install -r requirements.txt
python manage.py collectstatic --noinput

# Prefer direct Neon URL for migrations when provided (avoids pooler timeouts)
if [ -n "${DIRECT_DATABASE_URL:-}" ]; then
  DATABASE_URL="$DIRECT_DATABASE_URL" python manage.py migrate --noinput
else
  python manage.py migrate --noinput
fi
