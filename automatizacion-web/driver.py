import os
import logging
import random
import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv, set_key
from Logging import setup_logging
from UserAgentRotator import RandomUserAgent
from typing import Optional, Tuple, Any






class Driver:
    Locator = Tuple[str, str]
    def __init__(self, driver):
        self.driver = driver
        self.log = logging.getLogger(__name__)

    def _add_by(self, locator: tuple) -> tuple:
        k, v = locator
        if isinstance(k, str):
            return (getattr(By, k), v)
        return locator

    def open(self, url: str):
        self.log.info(f"Abrir URL: {url}")
        self.driver.get(url)

    def click(self, locator: tuple, timeout: int = 30):
        try:
            loc = self._add_by(locator)
            el = WebDriverWait(self.driver, timeout).until(EC.element_to_be_clickable(loc))
            el.click()
            self.log.debug(f"Click en {locator}")
        except Exception as e:
            self.log.error(f"Error al hacer click en {locator}: {e}")
            raise

    def type_in(self, locator: tuple, text: str, clear: bool = True, timeout: int = 30):
        try:
            loc = self._add_by(locator)
            el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(loc))
            if clear:
                el.clear()
            el.send_keys(text)
            self.log.debug(f"Tipeado en {locator}: {text}")
        except Exception as e:
            self.log.error(f"Error al tipear en {locator}: {e}")
            raise

    def get_text(self, locator: tuple, timeout: int = 30) -> str:
        try:
            loc = self._add_by(locator)
            el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(loc))
            txt = el.text.strip()
            self.log.debug(f"Texto de {locator}: {txt}")
            return txt
        except Exception as e:
            self.log.error(f"Error al obtener texto de {locator}: {e}")
            raise

    def check_visibility(self, locator: tuple, timeout: int = 10):
        loc = self._add_by(locator)
        return WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(loc))

    def check_existence(self, locator: tuple, timeout: int = 10) -> bool:
        try:
            loc = self._add_by(locator)
            WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(loc))
            return True
        except:
            return False

    def js_click(self, locator: tuple, timeout: int = 30):
        loc = self._add_by(locator)
        el = WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(loc))
        self.driver.execute_script("arguments[0].click();", el)

    def select_by_text(self, locator: tuple, visible_text: str, timeout: int = 30):
        loc = self._add_by(locator)
        Select(WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(loc))).select_by_visible_text(visible_text)

    def quit(self):
        self.log.info("Cerrando driver")
        self.driver.quit()



def create_chrome_driver(
    headless: bool = True,
    download_dir: Optional[str] = None,
    user_agent: Optional[str] = None,
    page_load_timeout: int = 30,
) -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    if user_agent:
        opts.add_argument(f"--user-agent={user_agent}")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1366,768")

    #se crea la carpeta de descargas dentro de nuestra carpeta actual, si existe, se usa la carpeta con ese nombre
    if download_dir:
        d = Path(download_dir)
        if not d.is_absolute():
            d = Path(__file__).parent / d
        download_path = d.resolve()
        download_path.mkdir(parents=True, exist_ok=True)
        prefs = {
            "download.default_directory": str(download_path),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True,
        }
        opts.add_experimental_option("prefs", prefs)


    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=opts)
    driver.set_page_load_timeout(page_load_timeout)
    return driver


def wait_for_downloads(folder: str | Path, timeout: int = 60, exts=(".xlsx", ".xls", ".csv", ".zip")) -> list[Path]:
    folder = Path(folder)
    end = time.time() + timeout
    last_complete = []

    while time.time() < end:
        files = list(folder.glob("*"))
        # Si hay algún .crdownload, seguimos esperando
        if any(f.suffix == ".crdownload" for f in files):
            time.sleep(1)
            continue
        # Filtramos por extensiones esperadas
        done = [f for f in files if f.suffix.lower() in exts]
        if done and done != last_complete:
            last_complete = done[:]
            # damos un pequeño margen
            time.sleep(1.5)
            return last_complete
        time.sleep(0.5)
    return last_complete



