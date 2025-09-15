# ETL – Parte 2 (Boxer)

Este repositorio contiene la solución de la **Parte 2 – ETL**. El script principal genera **datasets CSV** a partir de una base MySQL levantada con Docker. Se usan **consultas SQL puras** (sin ORM) y **pandas** para materializar las salidas.

---

## ¿Qué hace el script?

Ejecuta 4 tareas y escribe 4 CSV en la carpeta de salida:

1. **Autofix sin actualización**  
   `lista_a_actualizar_Autofix.csv` – Repuestos del proveedor **Autofix** cuyo precio **no** se actualizó en el **último mes** (o en los *últimos N días* con `--ultimos-dias`).
2. **Aumento 15% por marcas**  
   `aumento_15_marcas_seleccionadas.csv` – Propone **+15%** para marcas: `ELEXA`, `BERU`, `SH`, `MASTERFILT`, `RN`.
3. **Recargo 30% por proveedores y rango**  
   `aumento_productos.csv` – Propone **+30%** para proveedores **AutoRepuestos Express** y **Automax**, con precios **> 50.000** y **< 100.000**.
4. **Resumen por proveedor (legible)**  
   `datos_individuales_proveedores.csv` – Para cada proveedor: una **fila resumen** (totales, sin descripción, repuesto más caro) seguida de las **filas por marca** con su precio promedio. Formato pensado para lectura simple (sin repetir datos por cada marca).

> Todas las consultas a la base se realizan con **SQL puro** dentro de `main.py` y las salidas se crean con **pandas** (CSV).

---

## Estructura relevante

.
├─ docker-compose.yml
├─ mysql-init/
│  ├─ init-db.sh                # Script de inicialización para Linux
│  ├─ init-db-windows.sh        # Alternativa para Windows (ver abajo)
│  └─ repuestosDB_init.sql      # Datos de ejemplo
├─ mysql-data/                  # Datadir (se crea/borra localmente)
├─ respuestas/
│  └─ parte2/
│     ├─ main.py                # Script ETL (CLI)
│     ├─ runscript.sh           # Runner para Linux (bash)
│     └─ runscript.ps1          # Runner para Windows (PowerShell)
├─ requirements.txt
└─ .env                         # Credenciales de DB (no se commitean reales)

---

## Variables de entorno (`.env`)

Ejemplo de `.env` usado por `main.py`:

DB_HOST=localhost
DB_PORT=3306
DB_NAME=repuestosDB
DB_USER=scrapper
DB_PASS=6vT9pQ2sXz1L
DB_ROOT_PASS=y7Qp!2zLw9Vx

> Podés cambiar estos valores sin tocar el código. `main.py` los lee con `python-dotenv`.

---

## Levantar MySQL con Docker

1. **Primera vez o reinicio limpio**

docker compose down
rm -rf mysql-data
docker compose up -d --build

2. **Problemas comunes resueltos**
- **`bad interpreter: /bin/bash^M`**: el script del init tenía **CRLF** (Windows). Convertir a **LF** y dar permisos:
  sed -i 's/$//' mysql-init/init-db.sh
  chmod +x mysql-init/init-db.sh

- **`.sql` no encontrado**: usar **ruta absoluta** dentro del contenedor (ver ejemplo de `init-db-windows.sh`).
- **No se aplican cambios**: borrar `mysql-data` y recrear (Docker solo ejecuta `/docker-entrypoint-initdb.d` la **primera** vez).

### `init-db-windows.sh` (alternativa)

Si estás en Windows y te vuelve a aparecer el problema de CRLF o de rutas, podés usar este script y apuntarlo desde `docker-compose.yml` (se monta en `/docker-entrypoint-initdb.d`).

#!/usr/bin/env bash
set -euo pipefail
echo "Cargando datos iniciales en repuestosDB..."
mysql -u root -p"$MYSQL_ROOT_PASSWORD" repuestosDB < /docker-entrypoint-initdb.d/repuestosDB_init.sql
echo "Listo."

> Guardar con **LF**, no CRLF. Si se edita en Windows: “Cambiar fin de línea: LF” en VS Code.

---

## Cómo ejecutar el ETL

### 1) Windows (PowerShell)

pip install -r requirements.txt

.espuestas\parte2unscript.ps1 -OutDir .espuestas\parte2

python .espuestas\parte2\main.py --out .espuestas\parte2

### 2) Linux (bash)

pip install -r requirements.txt

chmod +x ./respuestas/parte2/runscript.sh
./respuestas/parte2/runscript.sh ./respuestas/parte2

python ./respuestas/parte2/main.py --out ./respuestas/parte2

### Parámetros útiles del CLI

- `--out` (**obligatorio**): carpeta donde guardar los CSV.  
- `--decimal` (`,|.`): separador decimal en CSV. *Default:* `,` (útil para Google Sheets en es-AR).  
- `--sep`: separador de columnas del CSV. *Default:* `,`.  
- `--ultimos-dias`: usa **N días exactos** en lugar de “un mes” para la condición de actualizaciones de Autofix. Ej.: `--ultimos-dias 30`.

python main.py --out ./respuestas/parte2 --ultimos-dias 30 --decimal "," --sep ","

---

## Complicaciones que se resolvieron

1. **`/bin/bash^M: bad interpreter`** al inicializar MySQL.  
   Motivo: archivos con **CRLF**. Solución: convertir a **LF** y `chmod +x` (o usar `init-db-windows.sh`).

2. **Scripts de init ignorados** tras hacer cambios.  
   Motivo: el datadir ya existía. Solución: `docker compose down && rm -rf mysql-data && docker compose up --build`.

3. **`.sql` no encontrado**.  
   Motivo: path relativo dentro del contenedor. Solución: usar la ruta absoluta `/docker-entrypoint-initdb.d/repuestosDB_init.sql`.

4. **Dificultades para correr `.sh` en Windows**.  
   Solución: se provee **`runscript.ps1`** (PowerShell) para Windows y **`runscript.sh`** para Linux.

5. **Números importados como texto en Google Sheets**.  
   Solución: los CSV se generan con columnas numéricas y `decimal=","` por defecto para que sean reconocidos como números en es-AR.

---

## Requisitos

- Docker + Docker Compose (para la base MySQL local).
- Python 3.10+ con `pip`.
- Paquetes: ver `requirements.txt`.

---

## Notas finales

- El script **no modifica** la base (solo `SELECT`).
- Los CSV se generan en la carpeta pasada por `--out`.
- Se dejan **dos runners**: `runscript.ps1` (Windows) y `runscript.sh` (Linux).
- Se incluye un **`init-db-windows.sh`** de referencia para reemplazar en `docker-compose` si reaparecen problemas de CRLF/rutas en Windows.
