#!/bin/sh

# Wait for PostgreSQL
set -e

host="$1"
shift
port="$1"
shift

# Wait for PostgreSQL to be ready
until echo "SELECT 1" | PGPASSWORD="${DB_PASSWORD}" psql -h "$host" -p "$port" -U "${DB_USER}" -d postgres -tA > /dev/null 2>&1; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
  echo "Retrying connection to Postgres..."
done

>&2 echo "Postgres is up - continuing"

# Execute the remaining arguments as a command
exec "$@"
