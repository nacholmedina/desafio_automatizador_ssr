#!/usr/bin/env bash
set -euo pipefail

echo "Ejecutando script SQL..."
mysql -u root -p"$MYSQL_ROOT_PASSWORD" repuestosDB < /docker-entrypoint-initdb.d/repuestosDB_init.sql
echo "Listo."