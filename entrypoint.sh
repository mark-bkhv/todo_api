#!/bin/sh
echo "Waiting for postgres...EP"
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

cd todorest
python manage.py flush --no-input
python manage.py migrate

exec "$@"