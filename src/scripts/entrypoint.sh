#!/usr/bin/env bash

set -o errexit
set -o pipefail
cmd="$@"

function postgres_ready(){
python << END

import sys
import psycopg2
import environ

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

env = environ.Env()
# 將 PosixPath 物件轉換為字串
environ.Env.read_env(str(BASE_DIR.joinpath('envs', 'base.env')))
environ.Env.read_env(str(BASE_DIR.joinpath('envs', env('USE_ENV'))))

try:
	dbname = env('POSTGRES_DB')
	user = env('POSTGRES_USER')
	password = env('POSTGRES_PASSWORD')
	host = env('POSTGRES_HOST')
	port = env('POSTGRES_PORT')
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
