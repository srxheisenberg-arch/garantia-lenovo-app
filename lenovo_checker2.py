import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from selenium.webdriver.chrome.service import Service as ChromeService

def get_element_text_or_none(driver, by, value):
    try:
        return driver.find_element(by, value).text
    except NoSuchElementException:
        return None

def check_lenovo_serial(serial_number):
    """
    Verifica una serie de Lenovo y extrae los detalles de la garantía.

    Args:
        serial_number (str): El número de serie a verificar.

    Returns:
        str: Un JSON con la información del producto o un mensaje de error.
    """
    options = webdriver.ChromeOptions()
    
    # Disfrazar el navegador headless
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36")
    options.add_argument("--window-size=1920,1080")
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = None
    try:
        # Configuración específica para Render
        if os.environ.get('RENDER'):
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            
            chrome_bin = os.environ.get('GOOGLE_CHROME_BIN')
            chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')

            if not chrome_bin or not chromedriver_path:
                return json.dumps({"error": "CONFIG_ERROR", "mensaje": "Las variables de entorno GOOGLE_CHROME_BIN o CHROMEDRIVER_PATH no están configuradas en Render."}, indent=4)

            options.binary_location = chrome_bin
            service = ChromeService(executable_path=chromedriver_path)
            driver = webdriver.Chrome(service=service, options=options)
        else:
            # Configuración para ejecución local (Selenium gestiona el driver)
            driver = webdriver.Chrome(options=options)

        driver.get("https://pcsupport.lenovo.com/cl/es/warranty-lookup#/")
        
        time.sleep(3)
        wait = WebDriverWait(driver, 30) # Aumentado a 30 segundos

        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "cookie-banner-ok-button")))
            cookie_button.click()
        except TimeoutException:
            pass

        # Localizar el campo de entrada, ingresar la serie y hacer clic en buscar
        input_field = wait.until(EC.presence_of_element_located((By.ID, "warranty_search_input")))
        input_field.send_keys(serial_number)

        submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "search_btn")))
        submit_button.click()

        # Esperar a que la página de resultados cargue o redirija
        # La página redirige a una URL específica del producto, donde la información de garantía
        # está incrustada en un objeto JavaScript llamado 'ds_warranties'.
        wait.until(EC.url_contains("products"))
        time.sleep(5) # Dar tiempo extra para que el JS se ejecute y el objeto esté disponible

        # Extraer el objeto JavaScript 'ds_warranties' directamente
        ds_warranties_json = driver.execute_script("return JSON.stringify(window.ds_warranties);")
        
        if not ds_warranties_json:
            return json.dumps({"error": "INVALIDO", "mensaje": "No se encontró el objeto ds_warranties en la página."}, indent=4)

        ds_warranties_data = json.loads(ds_warranties_json)

        # Verificar si hay información de garantía válida
        if not ds_warranties_data or not ds_warranties_data.get("BaseWarranties"):
            # Intentar buscar un mensaje de error si no hay garantías base
            error_message = get_element_text_or_none(driver, By.XPATH, '//*[contains(text(), "No se encontraron productos")]')
            if error_message:
                return json.dumps({"error": "INVALIDO", "mensaje": error_message}, indent=4)
            else:
                return json.dumps({"error": "INVALIDO", "mensaje": "Número de serie no encontrado o sin información de garantía."}, indent=4)

        # Extraer los datos relevantes
        product_name = ds_warranties_data.get("ProductName", "N/A")
        
        # El estado general de la garantía puede venir de ds_warranties.StatusV2 o de ds_warranties.BaseUpmaWarranties[0].StatusV2
        # O podemos inferirlo de la primera garantía base
        warranty_status_general = "N/A"
        if ds_warranties_data.get("BaseWarranties"):
            first_warranty = ds_warranties_data["BaseWarranties"][0]
            warranty_status_general = first_warranty.get("StatusV2", "N/A")
            
            # Detalles de la primera garantía base
            start_date = first_warranty.get("Start", "N/A")
            end_date = first_warranty.get("End", "N/A")
            status = first_warranty.get("StatusV2", "N/A")
            warranty_type = first_warranty.get("Name", "N/A")
        else:
            start_date = "N/A"
            end_date = "N/A"
            status = "N/A"
            warranty_type = "N/A"

        data = {
            "modelo": product_name,
            "estado_garantia_general": warranty_status_general,
            "detalles_garantia": {
                "fecha_inicio": start_date,
                "fecha_fin": end_date,
                "estado_especifico": status,
                "tipo": warranty_type
            }
        }
        
        return json.dumps(data, indent=4, ensure_ascii=False)

    except TimeoutException:
        return json.dumps({"error": "INVALIDO", "mensaje": "El número de serie no arrojó resultados (Timeout)."}, indent=4)
    except Exception as e:
        return json.dumps({"error": "ERROR", "mensaje": str(e)}, indent=4)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        serial = sys.argv[1]
    else:
        serial = input("Por favor, ingrese el número de serie: ")
    
    result = check_lenovo_serial(serial)
    print(result)