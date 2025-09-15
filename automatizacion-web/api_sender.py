from __future__ import annotations
from pathlib import Path
from datetime import datetime
import re
import logging
import requests
import time

from files_processor import process_all_in_downloads, DOWNLOAD_DIR
from Logging import setup_logging

API_URL = "https://desafio.somosait.com/api/upload/"

def _today_tag() -> str:
    return datetime.now().strftime("%Y%m%d")

def _list_provider_outputs(d: Path) -> set[Path]:
    pat = re.compile(rf"^(AutoRepuestos Express|Mundo RepCar|Autofix)_{_today_tag()}\.xlsx$", re.IGNORECASE)
    return {p for p in d.iterdir() if p.is_file() and p.suffix.lower()==".xlsx" and pat.match(p.name)}

def upload_file(path: Path, max_retries: int = 3, timeout: tuple[int, int] = (15, 600)) -> tuple[bool, str]:
    log = logging.getLogger(__name__)
    for attempt in range(1, max_retries + 1):
        try:
            with open(path, "rb") as f:
                r = requests.post(
                    API_URL,
                    files={"file": (path.name, f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
                    timeout=timeout,
                )
            if r.status_code == 200:
                try:
                    data = r.json()
                except Exception:
                    data = {}
                return True, data.get("link", "")
            else:
                try:
                    msg = r.json()
                except Exception:
                    msg = r.text
                log.warning(f"Intento {attempt}/{max_retries} al subir {path.name} -> {r.status_code}: {msg}")
        except requests.Timeout as e:
            log.warning(f"Intento {attempt}/{max_retries} timeout subiendo {path.name}: {e}")
        except Exception as e:
            log.exception(f"Intento {attempt}/{max_retries} error subiendo {path.name}: {e}")

        if attempt < max_retries:
            time.sleep(2 ** attempt)
        else:
            try:
                msg = r.json()
            except Exception:
                msg = r.text if 'r' in locals() else str(e)
            return False, f"{getattr(r, 'status_code', 'ERR')}: {msg}"


def upload_new_processed(download_dir=DOWNLOAD_DIR):
    log = logging.getLogger(__name__)
    d = Path(download_dir)
    before = _list_provider_outputs(d)
    log.debug(f"Salidas existentes antes de procesar: {[p.name for p in before]}")
    outs, proc_errs = process_all_in_downloads(d)
    after = _list_provider_outputs(d)
    log.debug(f"Salidas existentes después de procesar: {[p.name for p in after]}")
    new_outputs = sorted(after - before, key=lambda p: p.stat().st_mtime)
    log.info(f"Archivos nuevos detectados para subir: {[p.name for p in new_outputs]}")

    uploaded, failed = [], []
    for p in new_outputs:
        ok, info = upload_file(p)
        if ok:
            log.info(f"Subida OK: {p.name} -> {info}")
            uploaded.append((p.name, info))
        else:
            log.error(f"Fallo al subir {p.name}: {info}")
            failed.append((p.name, info))
    for name, msg in proc_errs:
        log.error(f"Error de procesamiento en {name}: {msg}")
    if not new_outputs and not proc_errs:
        log.info("No hay nuevos archivos para procesar ni subir.")
    return uploaded, failed, proc_errs

