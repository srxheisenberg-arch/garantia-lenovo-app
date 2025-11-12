import requests
import json

def check_lenovo_serial(serial_number):
    """
    (DEBUGGING VERSION)
    Verifica una serie de Lenovo y devuelve la respuesta cruda de la API para depuración.
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

        # Devolvemos directamente el JSON crudo de la respuesta para analizar su estructura.
        raw_data = response.json()
        return json.dumps(raw_data, indent=4, ensure_ascii=False)

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