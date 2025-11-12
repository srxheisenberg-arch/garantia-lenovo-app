
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_element_text_or_none(driver, by, value):
    try:
        return driver.find_element(by, value).text
    except NoSuchElementException:
        return None

def check_hp_serial(serial_number):
    """
    Verifica una serie de HP y extrae los detalles de la garantía.

    Args:
        serial_number (str): El número de serie a verificar.

    Returns:
        str: Un JSON con la información del producto o un mensaje de error.
    """
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Desactivado
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        # Minimizar la ventana justo después de crearla
        driver.minimize_window()
        
        url = f"https://support.hp.com/cl-es/product/details/hp-prodesk-405-g6-small-form-factor-pc/model/38230310?serialnumber={serial_number}"
        driver.get(url)
        
        wait = WebDriverWait(driver, 20)

        wait.until(EC.presence_of_element_located((By.XPATH, '//h1[@class="product-name-text"]')))
        time.sleep(2)

        product_name = get_element_text_or_none(driver, By.XPATH, '//h1[@class="product-name-text"]')
        warranty_status = get_element_text_or_none(driver, By.XPATH, '//div[contains(@class, "warranty-status-bar")]//div[@class="common"]')

        if not product_name:
            return json.dumps({"error": "INVALIDO", "mensaje": "Número de serie no encontrado."}, indent=4)

        data = {
            "modelo": product_name.strip() if product_name else "No encontrado",
            "estado_garantia": warranty_status.strip() if warranty_status else "No encontrado"
        }
        
        return json.dumps(data, indent=4, ensure_ascii=False)

    except TimeoutException:
        return json.dumps({"error": "INVALIDO", "mensaje": "El número de serie no arrojó resultados (Timeout). Revisa si la serie es correcta." }, indent=4)
    except Exception as e:
        return json.dumps({"error": "ERROR", "mensaje": str(e)}, indent=4)
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        serial = sys.argv[1]
    else:
        serial = input("Por favor, ingrese el número de serie de HP: ")
    
    result = check_hp_serial(serial)
    print(result)
