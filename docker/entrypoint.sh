#!/usr/bin/env sh
set -e

echo "Waiting for Postgres at ${POSTGRES_HOST}:${POSTGRES_PORT}..."
python - <<'PY'
import os, time
import psycopg

host = os.environ.get("POSTGRES_HOST", "db")
port = int(os.environ.get("POSTGRES_PORT", "5432"))
dbname = os.environ.get("POSTGRES_DB", "team_finder")
user = os.environ.get("POSTGRES_USER", "team_finder")
password = os.environ.get("POSTGRES_PASSWORD", "team_finder")

deadline = time.time() + 60
last_err = None
while time.time() < deadline:
    try:
        conn = psycopg.connect(
            host=host, port=port, dbname=dbname, user=user, password=password, connect_timeout=2
        )
        conn.close()
        print("Postgres is available.")
        raise SystemExit(0)
    except Exception as e:
        last_err = e
        time.sleep(1)

print("Postgres is not available:", last_err)
raise SystemExit(1)
PY

python manage.py migrate --noinput

exec python manage.py runserver 0.0.0.0:8000

