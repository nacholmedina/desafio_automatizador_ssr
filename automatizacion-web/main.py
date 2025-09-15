from __future__ import annotations
import logging
from pathlib import Path
from dotenv import load_dotenv
from Logging import setup_logging

from UserAgentRotator import RandomUserAgent
from driver import create_chrome_driver, Driver
from files_downloader import (
    download_autorepuestos_express,
    download_mundo_repcar,
    download_autofix_all_brands,
)
from files_processor import process_all_in_downloads, DOWNLOAD_DIR
from api_sender import upload_file


def main():
    setup_logging()
    load_dotenv(Path(__file__).parent.parent / ".env")
    log = logging.getLogger(__name__)

    driver_setup = create_chrome_driver(
        headless=True,
        download_dir=DOWNLOAD_DIR,
        user_agent=RandomUserAgent(),
        page_load_timeout=30,
    )
    driver = Driver(driver_setup)

    try:
        driver.open("https://desafiodataentryait.vercel.app/")
        try:
            download_autorepuestos_express(driver, DOWNLOAD_DIR)
            download_mundo_repcar(driver, DOWNLOAD_DIR)
            download_autofix_all_brands(driver, DOWNLOAD_DIR)
            log.info("Descargas completadas")
        except Exception as e:
            log.exception(f"Fallo durante descargas: {e}")
    except Exception as e:
        log.exception(f"No se pudo abrir el sitio: {e}")
    try:
        driver.quit()
    except Exception:
        pass

    outs, errs = process_all_in_downloads(DOWNLOAD_DIR)
    for name, msg in errs:
        logging.getLogger(__name__).error(f"Error de procesamiento en {name}: {msg}")

    if outs:
        log.info(f"Archivos procesados en esta ejecución: {[Path(p).name for p in outs]}")
    else:
        log.info("No se generaron archivos procesados en esta ejecución")

    uploaded_ok, uploaded_fail = [], []
    for p in outs:
        ok, info = upload_file(Path(p))
        if ok:
            log.info(f"Subida OK: {Path(p).name} -> {info}")
            uploaded_ok.append((Path(p).name, info))
        else:
            log.error(f"Fallo al subir {Path(p).name}: {info}")
            uploaded_fail.append((Path(p).name, info))


if __name__ == "__main__":
    main()
