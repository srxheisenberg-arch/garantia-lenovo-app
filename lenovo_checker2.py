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

def check_lenovo_serial(serial_number):
    """
    Verifica una serie de Lenovo y extrae los detalles de la garantía.

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
        # Minimizar la ventana
        driver.minimize_window()

        driver.get("https://pcsupport.lenovo.com/cl/es/warranty-lookup#/")
        
        time.sleep(3)
        wait = WebDriverWait(driver, 20)

        try:
            cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "cookie-banner-ok-button")))
            cookie_button.click()
        except TimeoutException:
            pass

        serial_input = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "button-placeholder__input")))
        serial_input.send_keys(serial_number)
        
        submit_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'ENVIAR')]")))
        submit_button.click()

        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "prod-name")))
        time.sleep(2)

        product_name = get_element_text_or_none(driver, By.XPATH, '//div[@class="prod-name"]/h4')
        warranty_status = get_element_text_or_none(driver, By.XPATH, '//span[@class="warranty-status-right"]')
        start_date = get_element_text_or_none(driver, By.XPATH, '//div[contains(@class, "detail-property")]/span[contains(text(), "Fecha de inicio")]/following-sibling::span')
        end_date = get_element_text_or_none(driver, By.XPATH, '//div[contains(@class, "detail-property")]/span[contains(text(), "Fecha fin")]/following-sibling::span')
        status = get_element_text_or_none(driver, By.XPATH, '//div[contains(@class, "detail-property")]/span[contains(text(), "Estado")]/following-sibling::span')
        warranty_type = get_element_text_or_none(driver, By.XPATH, '//div[contains(@class, "detail-property")]/span[contains(text(), "Tipo")]/following-sibling::span')

        if not product_name:
            error_message = get_element_text_or_none(driver, By.XPATH, '//*[contains(text(), "No se encontraron productos")]')
            if error_message:
                return json.dumps({"error": "INVALIDO", "mensaje": error_message}, indent=4)
            else:
                return json.dumps({"error": "INVALIDO", "mensaje": "Número de serie no encontrado, pero no se mostró un mensaje de error claro."}, indent=4)

        data = {
            "modelo": product_name,
            "estado_garantia_general": warranty_status,
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