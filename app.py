from flask import Flask, request, render_template_string, jsonify
from lenovo_checker2 import check_lenovo_serial
import json

app = Flask(__name__)

# HTML para el formulario y la página de resultados
HTML_TEMPLATE = '''
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  <title>Consulta de Garantía Lenovo</title>
  <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css">
  <style>
    body { background-color: #f8f9fa; }
    .container { max-width: 600px; margin-top: 50px; }
    .card { padding: 2rem; }
    pre { white-space: pre-wrap; word-wrap: break-word; }
  </style>
</head>
<body>
  <div class="container">
    <div class="card shadow-sm">
      <h3 class="text-center mb-4">Consulta de Garantía Lenovo</h3>
      <form method="post">
        <div class="form-group">
          <input type="text" name="serie" class="form-control" placeholder="Ingrese el número de serie" required>
        </div>
        <button type="submit" class="btn btn-primary btn-block">Consultar</button>
      </form>
      
      {% if resultado %}
      <hr>
      <h5 class="mt-4">Resultado:</h5>
      <pre class="bg-light p-3 rounded"><code>{{ resultado }}</code></pre>
      {% endif %}
    </div>
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    resultado = None
    if request.method == 'POST':
        serial_number = request.form.get('serie')
        if serial_number:
            # Llamamos a la función y obtenemos el string JSON
            resultado_json_str = check_lenovo_serial(serial_number)
            # Formateamos el JSON para mostrarlo bonito
            parsed_json = json.loads(resultado_json_str)
            resultado = json.dumps(parsed_json, indent=4, ensure_ascii=False)

    return render_template_string(HTML_TEMPLATE, resultado=resultado)

@app.route('/consultar', methods=['GET'])
def consultar_api():
    """
    Endpoint de la API para mantener compatibilidad.
    """
    serial_number = request.args.get('serie')
    if not serial_number:
        return jsonify({"error": "El parámetro 'serie' es requerido."}), 400
    
    result_json_str = check_lenovo_serial(serial_number)
    result_data = json.loads(result_json_str)
    return jsonify(result_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)