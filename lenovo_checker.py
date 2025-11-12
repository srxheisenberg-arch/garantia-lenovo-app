import requests
import json

def check_lenovo_serial(serial_number):
    """
    Verifica una serie de Lenovo y extrae los detalles de la garantía usando la API de pcsupport.

    Args:
        serial_number (str): El número de serie a verificar.

    Returns:
        str: Un JSON con la información del producto o un mensaje de error.
    """
    if not serial_number:
        return json.dumps({"error": "INVALIDO", "mensaje": "El número de serie no puede estar vacío."}, indent=4)

    api_url = f"https://pcsupport.lenovo.com/cl/es/api/v4/mse/getproducts?productId={serial_number}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        response.raise_for_status()

        data = response.json()

        if not data or not isinstance(data, list) or not data[0].get("Name"):
            return json.dumps({"error": "INVALIDO", "mensaje": "Número de serie no encontrado o respuesta inesperada de la API."}, indent=4)

        product_info = data[0]
        
        # Inicializamos los datos de garantía
        warranty_details = {
            "fecha_inicio": None,
            "fecha_fin": None,
            "estado_especifico": None,
            "tipo": None
        }
        estado_garantia_general = "No disponible"

        # Intentamos encontrar la información de garantía de forma más robusta
        # Buscamos en las claves más comunes
        for key, value in product_info.items():
            if isinstance(value, list) and key.lower() in ["warranty", "warranties", "coverage"]:
                for item in value:
                    if isinstance(item, dict):
                        # Asumimos que el primer elemento con fechas es la garantía principal
                        if item.get("StartDate") and item.get("EndDate"):
                            warranty_details["fecha_inicio"] = item.get("StartDate")
                            warranty_details["fecha_fin"] = item.get("EndDate")
                            warranty_details["estado_especifico"] = item.get("Status")
                            warranty_details["tipo"] = item.get("Type")
                            estado_garantia_general = item.get("Status", "No disponible")
                            break # Tomamos la primera garantía válida y salimos
                if estado_garantia_general != "No disponible":
                    break # Si encontramos garantía, salimos del bucle de claves

        final_data = {
            "modelo": product_info.get("Name", "No encontrado"),
            "estado_garantia_general": estado_garantia_general,
            "detalles_garantia": warranty_details
        }
        
        return json.dumps(final_data, indent=4, ensure_ascii=False)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": "ERROR_RED", "mensaje": f"Error de conexión al consultar la API: {e}"}, indent=4)
    except Exception as e:
        return json.dumps({"error": "ERROR_INESPERADO", "mensaje": f"Ocurrió un error inesperado: {e}"}, indent=4)

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        serial = sys.argv[1]
    else:
        serial = input("Por favor, ingrese el número de serie: ")
    
    result = check_lenovo_serial(serial)
    print(result)
