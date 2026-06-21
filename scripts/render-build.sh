#!/usr/bin/env bash
set -euo pipefail

pip install -r requirements.txt
python manage.py collectstatic --noinput

# Migrations must use Neon's DIRECT URL (not the pooler). Auto-derive if needed.
migrate_url="${DIRECT_DATABASE_URL:-${DATABASE_URL:-}}"

if [ -z "$migrate_url" ]; then
  echo "ERROR: DATABASE_URL is not set."
  exit 1
fi

if [[ "$migrate_url" == *"-pooler"* ]]; then
  migrate_url="${migrate_url//-pooler/}"
  echo "Using direct Neon host for migrate (stripped -pooler from DATABASE_URL)."
fi

if [[ "$migrate_url" != *"sslmode="* ]]; then
  if [[ "$migrate_url" == *"?"* ]]; then
    migrate_url="${migrate_url}&sslmode=require"
  else
    migrate_url="${migrate_url}?sslmode=require"
  fi
fi

attempt=1
max_attempts=5
until DATABASE_URL="$migrate_url" python manage.py migrate --noinput; do
  if [ "$attempt" -ge "$max_attempts" ]; then
    echo "migrate failed after ${max_attempts} attempts."
    exit 1
  fi
  echo "migrate attempt ${attempt} failed — retrying in 5s (Neon may be waking up)..."
  sleep 5
  attempt=$((attempt + 1))
done

echo "migrate completed successfully."
