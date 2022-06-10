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
  if [ -z "${SITE_URL}" ]; then
    echo "You need to specify SITE_URL for oauth!"
    exit 1
  fi
  echo "Using Public URL: ${SITE_SCHEMA:=https}://${SITE_URL}:${SITE_PORT:=443}"
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

# verify wireguard peer manager specific environment variables exist
failed=0
if [ -z "${WG_DESCRIPTION}" ]; then
  echo "Missing environment variable: WG_DESCRIPTION"
  failed=1
fi
if [ -z "${WG_PUBKEY}" ]; then
  echo "Missing environment variable: WG_PUBKEY"
  failed=1
fi
if [ -z "${WG_ENDPOINT}" ]; then
  echo "Missing environment variable: WG_ENDPOINT"
  failed=1
fi
if [ -z "${WG_IPV4_NETWORK}" ]; then
  echo "Missing environment variable: WG_IPV4_NETWORK"
  failed=1
fi
if [ -z "${WG_IPV6_PREFIX}" ]; then
  echo "Missing environment variable: WG_IPV6_PREFIX"
  failed=1
fi
if [ ${failed} -ne 0 ]; then
  exit 1
fi


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
