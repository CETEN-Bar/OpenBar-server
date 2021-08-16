#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER service_example PASSWORD '$DB_SERVICE_EXAMPLE_PW';
    CREATE DATABASE "example";
    GRANT ALL PRIVILEGES ON DATABASE "example" TO service_example;

    CREATE USER service_user PASSWORD '$DB_SERVICE_USER_PW';
    CREATE DATABASE "user";
    GRANT ALL PRIVILEGES ON DATABASE "user" TO service_user;
EOSQL
