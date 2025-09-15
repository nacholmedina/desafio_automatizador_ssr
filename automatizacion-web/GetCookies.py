import os
import logging
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv, set_key
from Logging import setup_logging
from UserAgentRotator import RandomUserAgent

def CookieGetter():
    load_dotenv()


    user_id = os.getenv("USER_ID")
    password = os.getenv("PASSWORD")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument(f"user-agent={RandomUserAgent()}")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        login_url = "https://wsec06.bancogalicia.com.ar/Users/Login"
        driver.get(login_url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "UserID"))
        )

        driver.find_element(By.ID, "UserID").send_keys(user_id)
        driver.find_element(By.ID, "password").send_keys(password)
        driver.find_element(By.ID, "submitButton").click()

        cookies = driver.get_cookies()

        skywalker_token = None
        skywalker_officebanking_token = None
        request_verification_token = None

        for cookie in cookies:
            if cookie['name'] == 'Skywalker':
                skywalker_token = cookie['value']
            elif cookie['name'] == 'Skywalker_officebanking':
                skywalker_officebanking_token = cookie['value']
            elif cookie['name'] == '__RequestVerificationToken':
                request_verification_token = cookie['value']


        if skywalker_token:
            set_key(".env", "SKYWALKER_TOKEN", skywalker_token)
            logging.info('Nuevo skywalker token añadido')
        if skywalker_officebanking_token:
            set_key(".env", "SKYWALKER_OFFICEBANKING_TOKEN", skywalker_officebanking_token)
            logging.info('Nuevo skywalker officebanking token añadido')

        # Este token no lo usamos pero lo obtenemos porque puede ser util para futuras solicitudes
        if request_verification_token:
            set_key(".env", "REQUEST_VERIFICATION_TOKEN", request_verification_token)
            logging.info('Nuevo request verification token añadido')

    finally:
        driver.quit()
