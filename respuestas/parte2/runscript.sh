#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-./respuestas/parte2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if   [[ -f "$SCRIPT_DIR/main.py" ]]; then
  MAIN_PY="$SCRIPT_DIR/main.py"
elif [[ -f "$SCRIPT_DIR/respuestas/parte2/main.py" ]]; then
  MAIN_PY="$SCRIPT_DIR/respuestas/parte2/main.py"
elif [[ -f "$SCRIPT_DIR/../main.py" ]]; then
  MAIN_PY="$(cd "$SCRIPT_DIR/.." && pwd)/main.py"
elif [[ -f "$SCRIPT_DIR/../../main.py" ]]; then
  MAIN_PY="$(cd "$SCRIPT_DIR/../.." && pwd)/main.py"
elif [[ -f "$(pwd)/main.py" ]]; then
  MAIN_PY="$(pwd)/main.py"
elif [[ -f "$(pwd)/../main.py" ]]; then
  MAIN_PY="$(cd .. && pwd)/main.py"
else
  echo "No se encontró main.py. Colocá runscript.sh en la misma carpeta que main.py o ajustá la ruta." >&2
  exit 1
fi

# Cargar variables desde .env si existe (al lado del .sh o del main.py)
if [[ -f "$SCRIPT_DIR/.env" ]]; then
  set -a; . "$SCRIPT_DIR/.env"; set +a
elif [[ -f "$(dirname "$MAIN_PY")/.env" ]]; then
  set -a; . "$(dirname "$MAIN_PY")/.env"; set +a
fi


mkdir -p "$OUT_DIR"

if [[ -f "$SCRIPT_DIR/requirements.txt" ]]; then
  python -m pip install -r "$SCRIPT_DIR/requirements.txt"
elif [[ -f "$(dirname "$MAIN_PY")/requirements.txt" ]]; then
  python -m pip install -r "$(dirname "$MAIN_PY")/requirements.txt"
fi

python "$MAIN_PY" --out "$OUT_DIR"

echo "CSV generados en: $OUT_DIR"
