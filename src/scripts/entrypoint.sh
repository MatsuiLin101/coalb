#!/usr/bin/env bash

set -o errexit
set -o pipefail
cmd="$@"

function postgres_ready(){
python << END

import environ
import psycopg2
import sys

BASE_DIR = environ.Path(__file__) - 1

env = environ.Env()
environ.Env.read_env(str(BASE_DIR.path('envs', 'base.env')))
environ.Env.read_env(str(BASE_DIR.path('envs', env.str('ENV_NAME'))))

try:
	dbname = env.str('POSTGRES_DB')
	user = env.str('POSTGRES_USER')
	password = env.str('POSTGRES_PASSWORD')
	host = env.str('POSTGRES_HOST')
	port = env.int('POSTGRES_PORT')

	print(f"dbname is {dbname}")
	print(f"user is {user}")
	print(f"password is {password}")
	print(f"host is {host}")
	print(f"port is {port}")

	conn = psycopg2.connect(dbname=dbname, user=user, password=password, host=host, port=port)
except psycopg2.OperationalError as e:
	sys.exit(-1)
sys.exit(0)
END
}

until postgres_ready; do
	>&2 echo "Postgres is unavailable - sleeping"
	sleep 1
done

>&2 echo "Postgres is up - continuing..."
exec $cmd
