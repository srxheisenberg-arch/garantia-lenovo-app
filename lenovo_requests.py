import requests
import re
import json
import sys

def check_lenovo_serial_requests(serial_number):
    """
    Verifica una serie de Lenovo y extrae los detalles de la garantía usando solo requests
    y extrayendo los datos del HTML de la página final.
    """
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
    }
    
    # URL de la página de consulta. Usamos /us/en para ser genéricos.
    lookup_url = "https://pcsupport.lenovo.com/us/en/warranty-lookup#/"
    
    try:
        # 1. Visitar la página para obtener cookies y estado de sesión
        session.get(lookup_url, headers=headers, timeout=10)
        
        # 2. Enviar el número de serie como datos de formulario a la misma URL.
        # La sesión de requests seguirá la redirección automáticamente.
        payload = {'serialNumber': serial_number}
        response = session.post(lookup_url, headers=headers, data=payload, timeout=15)
        
        response.raise_for_status()
        
        # 3. Extraer el objeto ds_warranties del HTML de la página final
        html_content = response.text
        
        match = re.search(r"window\.ds_warranties\s*=\s*({.*?});", html_content, re.DOTALL)
        
        if not match:
            # Si no encontramos el objeto, puede que el número de serie sea inválido.
            if "No products found" in html_content or "Cannot find the product" in html_content:
                return json.dumps({"error": "INVALIDO", "mensaje": "Número de serie no encontrado."}, indent=4)
            return json.dumps({"error": "PARSE_ERROR", "mensaje": "No se pudo encontrar el objeto de garantía en la página. El sitio puede haber cambiado."}, indent=4)

        # 4. Limpiar y cargar el JSON
        json_str = match.group(1)
        ds_warranties_data = json.loads(json_str)

        # 5. Analizar y formatear los datos extraídos
        if not ds_warranties_data or not ds_warranties_data.get("BaseWarranties"):
            return json.dumps({"error": "INVALIDO", "mensaje": "Número de serie no encontrado o sin información de garantía."}, indent=4)

        product_name = ds_warranties_data.get("ProductName", "N/A")
        
        first_warranty = ds_warranties_data["BaseWarranties"][0]
        warranty_status_general = first_warranty.get("StatusV2", "N/A")
        start_date = first_warranty.get("Start", "N/A")
        end_date = first_warranty.get("End", "N/A")
        status = first_warranty.get("StatusV2", "N/A")
        warranty_type = first_warranty.get("Name", "N/A")

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

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": "REQUEST_ERROR", "mensaje": f"Error de conexión: {e}"}, indent=4)
    except Exception as e:
        return json.dumps({"error": "ERROR", "mensaje": str(e)}, indent=4)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        serial = sys.argv[1]
    else:
        serial = input("Por favor, ingrese el número de serie: ")
    
    result = check_lenovo_serial_requests(serial)
    print(result)
