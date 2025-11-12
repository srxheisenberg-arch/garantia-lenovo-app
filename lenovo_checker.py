import requests
import json

def check_lenovo_serial(serial_number):
    """
    Verifica una serie de Lenovo y extrae los detalles de la garantía usando una API.

    Args:
        serial_number (str): El número de serie a verificar.

    Returns:
        str: Un JSON con la información del producto o un mensaje de error.
    """
    if not serial_number:
        return json.dumps({"error": "INVALIDO", "mensaje": "El número de serie no puede estar vacío."}, indent=4)

    api_url = f"https://newthink.lenovo.com.cn/api/ThinkHome/Machine/WarrantyListInfo?sn={serial_number}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(api_url, headers=headers, timeout=20)
        response.raise_for_status()  # Lanza un error para respuestas 4xx/5xx

        data = response.json()

        # La API devuelve '1' si la serie es inválida.
        if data.get("code") != "0":
            return json.dumps({"error": "INVALIDO", "mensaje": data.get("msg", "Número de serie no encontrado.")}, indent=4)

        warranty_info = data.get("data", [])
        if not warranty_info:
            return json.dumps({"error": "INVALIDO", "mensaje": "No se encontraron detalles de garantía para este número de serie."}, indent=4)

        # Asumimos que la información principal está en el primer elemento
        info = warranty_info[0]
        
        # Mapeamos los campos de la API a la estructura de datos original
        # La API china no provee un nombre de modelo claro, usamos la serie.
        # Tampoco provee un estado general, lo deducimos.
        final_data = {
            "modelo": f"Modelo para SN: {serial_number}",
            "estado_garantia_general": "En Garantía" if info.get("inWarranty") == "1" else "Fuera de Garantía",
            "detalles_garantia": {
                "fecha_inicio": info.get("start_date"),
                "fecha_fin": info.get("end_date"),
                "estado_especifico": "Activa" if info.get("inWarranty") == "1" else "Expirada",
                "tipo": info.get("name", "No especificado")
            }
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
