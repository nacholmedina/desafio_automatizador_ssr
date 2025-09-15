import os
import time
from dotenv import load_dotenv
from pathlib import Path
from datetime import datetime
from Logging import setup_logging
from driver import create_chrome_driver, Driver, wait_for_downloads
from UserAgentRotator import RandomUserAgent

setup_logging()
load_dotenv(Path(__file__).parent.parent / ".env")

DOWNLOAD_DIR = Path(__file__).parent / "downloads"


user_id = os.getenv("USER_ID")
password = os.getenv("PASSWORD")
driver_setup = create_chrome_driver(
    headless=True,
    download_dir=DOWNLOAD_DIR,
    user_agent=RandomUserAgent(),
    page_load_timeout=30,
)
driver = Driver(driver_setup)

def open_desafio_site(driver):
    driver.open("https://desafiodataentryait.vercel.app/")

#Se ronombran todos los archivos descargados agregando timestamp, si el nombre contiene "AutoRepuestos Express" se reemplaza por "Mundo Repcar".
#Ya que hay un error en el nombre de esa lista
def rename_with_timestamp(file_path: str | Path, brand: str | None = None) -> Path:
    p = Path(file_path)
    stem = p.stem
    if "AutoRepuestos Express" in stem and "AutoRepuestos Express Lista de Precios" not in stem:
        stem = stem.replace("AutoRepuestos Express", "Mundo Repcar")
    if brand:
        b = "".join(ch for ch in brand.strip() if ch.isalnum() or ch in (" ", "_", "-")).replace(" ", "_")
        if b:
            stem = f"{stem}_{b}"
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    new_path = p.with_name(f"{stem}_{ts}{p.suffix}")
    p.rename(new_path)
    return new_path

def wait_overlay_gone(driver, timeout=120):
    start = time.time()
    while True:
        try:
            driver.check_visibility(('ID', 'loading-overlay'), timeout=1)
            visible = True
        except Exception:
            visible = False
        if not visible:
            return
        if time.time() - start > timeout:
            raise TimeoutError("loading-overlay no desapareció a tiempo")
        time.sleep(0.2)

def wait_overlay_appear(driver, timeout=10):
    start = time.time()
    while True:
        try:
            driver.check_visibility(('ID', 'loading-overlay'), timeout=1)
            return
        except Exception:
            if time.time() - start > timeout:
                return
            time.sleep(0.2)

def ensure_logged_in(driver, user_id: str, password: str):
    url = driver.driver.current_url
    if "/login" in url:
        driver.type_in(('ID', 'username'), user_id, timeout=10)
        driver.type_in(('ID', 'password'), password, timeout=10)
        driver.click(('CSS_SELECTOR', '.login-button'), timeout=10)


def download_autorepuestos_express(driver, download_dir=DOWNLOAD_DIR):
    before = {p.name for p in Path(download_dir).glob("*.xls*")}
    try:
        driver.click(('ID', 'download-button-autorepuestos-express'), timeout=20)
        _ = wait_for_downloads(download_dir, timeout=60, exts=(".xls", ".xlsx"))
        after = [p for p in Path(download_dir).glob("*.xls*")]
        new_files = [p for p in after if p.name not in before]
        if not new_files and after:
            new_files = [max(after, key=lambda p: p.stat().st_mtime)]
        if not new_files:
            raise RuntimeError(f"No se descargó ningún archivo nuevo en {download_dir}")
        renamed = [rename_with_timestamp(f) for f in new_files]
        print([str(p) for p in renamed])
        return renamed
    except Exception as e:
        raise e


def download_mundo_repcar(driver, download_dir=DOWNLOAD_DIR):
    before = {p.name for p in Path(download_dir).glob("*.csv")} | {p.name for p in Path(download_dir).glob("*.xls*")}
    try:
        driver.click(('ID', 'download-button-mundo-repcar'), timeout=15)
        ensure_logged_in(driver, user_id, password)
        driver.click(('CSS_SELECTOR', 'a.download-link'), timeout=20)
        _ = wait_for_downloads(download_dir, timeout=60, exts=(".csv", ".xls", ".xlsx"))
        after = [p for p in Path(download_dir).glob("*.csv")] + [p for p in Path(download_dir).glob("*.xls*")]
        new_files = [p for p in after if p.name not in before]
        if not new_files and after:
            new_files = [max(after, key=lambda p: p.stat().st_mtime)]
        if not new_files:
            raise RuntimeError(f"No se descargó ningún archivo nuevo en {download_dir}")
        renamed = [rename_with_timestamp(f) for f in new_files]
        print([str(p) for p in renamed])
        return renamed
    except Exception as e:
        raise e

def download_autofix_all_brands(driver, download_dir=DOWNLOAD_DIR):
    dl = Path(download_dir)
    exts = (".xlsx", ".xls", ".csv")

    if not driver.check_existence(('ID', 'download-button-autofix'), timeout=5):
        driver.open("https://desafiodataentryait.vercel.app/")
        driver.check_existence(('ID', 'download-button-autofix'), timeout=15)

    wait_overlay_gone(driver, timeout=60)

    try:
        driver.click(('ID', 'download-button-autofix'), timeout=10)
    except:
        wait_overlay_gone(driver, timeout=60)
        driver.js_click(('ID', 'download-button-autofix'), timeout=10)

    ensure_logged_in(driver, user_id, password)

    driver.check_visibility(('ID', 'brands-checkboxes'), timeout=20)
    wait_overlay_gone(driver, timeout=60)

    renamed_all = []
    i = 1
    while True:
        chk = ('ID', f'marca-{i}')
        if not driver.check_existence(chk, timeout=2):
            break

        driver.js_click(chk, timeout=10)
        brand_text = driver.get_text(('CSS_SELECTOR', f"label[for='marca-{i}']"), timeout=10)

        before = {p.name for p in dl.glob("*") if p.suffix.lower() in exts}

        wait_overlay_gone(driver, timeout=300)
        try:
            driver.click(('CSS_SELECTOR', 'button.bg-blue-600.border-blue-600'), timeout=15)
        except:
            wait_overlay_gone(driver, timeout=300)
            driver.js_click(('CSS_SELECTOR', 'button.bg-blue-600.border-blue-600'), timeout=15)

        wait_overlay_appear(driver, timeout=5)
        wait_overlay_gone(driver, timeout=300)

        _ = wait_for_downloads(dl, timeout=300, exts=exts)

        after = [p for p in dl.glob("*") if p.suffix.lower() in exts]
        new_files = [p for p in after if p.name not in before]
        if not new_files and after:
            new_files = [max(after, key=lambda p: p.stat().st_mtime)]

        for f in new_files:
            renamed_all.append(rename_with_timestamp(f, brand_text))

        driver.js_click(chk, timeout=10)
        wait_overlay_gone(driver, timeout=60)

        i += 1

    return renamed_all
