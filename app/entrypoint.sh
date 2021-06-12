#!/bin/sh

# check if required environment variables exist:
# shellcheck disable=SC2153

# set environment variables for database configuration (engine / port)
case ${ENV_DBMS} in
"mariadb")
  export SQL_ENGINE=django.db.backends.mysql
  # only set port if SQL_PORT hasn't been overwritten using the docker environment variables
  if [ -z "${SQL_PORT}" ]; then
    export SQL_PORT=3306
  fi
  ;;
"postgres")
  export SQL_ENGINE=django.db.backends.postgresql
  # only set port if SQL_PORT hasn't been overwritten using the docker environment variables
  if [ -z "${SQL_PORT}" ]; then
    export SQL_PORT=5432
  fi
  ;;
"sqlite3")
  export SQL_ENGINE=django.db.backends.sqlite3
  ;;
*)
  echo "Error ENV_DBMS=${ENV_DBMS} is undefined!"
  exit 1
  ;;
esac

case ${ENV_AUTH} in
"oauth")
  if [ -z "${PUBLIC_URL}" ]; then
    echo "You need to specify PUBLIC_URL for oauth!"
    exit 1
  fi
  echo "Using Public URL: ${SCHEMA}://${PUBLIC_URL}"
  ;;
esac

# wait for database
if [ "${ENV_DBMS}" != "sqlite3" ]; then
    if [ -z "${SQL_HOST}" ]; then
        echo "You need to specify SQL_HOST"
        exit 1
    fi
    echo "Waiting for ${ENV_DBMS}..."

    # shellcheck disable=SC2153
    while ! nc -z "${SQL_HOST}" "${SQL_PORT}"; do
        sleep 0.1
    done

    echo "${ENV_DBMS} started"
fi

python manage.py migrate

# shellcheck disable=SC2198
if [ -z "${@}" ]; then
  if [ "${DEBUG}" != 0 ]; then
    gunicorn app.wsgi:application --bind 0.0.0.0:8000 --log-level DEBUG
  else
    gunicorn app.wsgi:application --bind 0.0.0.0:8000
  fi
else
  exec "${@}"
fi
