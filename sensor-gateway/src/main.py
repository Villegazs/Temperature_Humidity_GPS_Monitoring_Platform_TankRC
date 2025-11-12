from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# URL de plantilla para Orion. Usamos "{}" como marcador de posición para el ID del sensor.
URL_DESTINO_TEMPLATE = "http://orion:1026/v2/entities/{}/attrs"

# Token secreto esperando para validación
TOKEN_SECRETO = "secreto"

# Cambiamos la ruta para que acepte un ID de sensor dinámico
@app.route('/recibirdatos/<sensor_id>', methods=['POST'])
def recibir_datos(sensor_id):
    """
    Recibe datos JSON, valida un token y reenvía los datos (sin token)
    como un PATCH al sensor especificado en la URL.
    """
    
    # Construye la URL de destino específica para este sensor
    url_destino = URL_DESTINO_TEMPLATE.format(sensor_id)
    
    # Intenta obtener el JSON de la solicitud
    try:
        datos = request.get_json(force=True) # force=True permite analizar el JSON sin el encabezado 'application/json'
    except Exception as e:
        print(f"Error al parsear JSON: {e}")
        return jsonify({"error": "Formato JSON inválido"}), 400
    
    # Valida la estructura del JSON
    if not isinstance(datos, dict):
        return jsonify({"error": "El cuerpo de la solicitud no es un objeto JSON"}), 400
    
    # Valida el token
    token_recibido = datos.get("token")
    if token_recibido != TOKEN_SECRETO:
        print(f"Token incorrecto recibido: {token_recibido}")
        return jsonify({"error": "Token de autenticacion incorrecto"}), 401
    
    # Si el token es correcto
    print(f"Datos recibidos para sensor '{sensor_id}' y validados correctamente.")
    
    # Elimina el token para no reenviarlo
    datos_sin_token = datos.copy()
    datos_sin_token.pop("token", None)
    
    print(f"Enviando PATCH a {url_destino} con datos: {datos_sin_token}")

    # Manda un patch a la url de destino dinámica
    try:
        response = requests.patch(url_destino, json=datos_sin_token)
        response.raise_for_status() # Lanza una excepcion si la solicitud falla
        print(f"Escritura exitosa a {url_destino}. Respuesta: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error al enviar PATCH a {url_destino}: {e}")
        return jsonify({"mensaje": "Datos recibidos, pero falló el reenvío", "error": str(e)}), 202
    
    return jsonify({"mensaje": "Datos recibidos y procesados correctamente."}), 200

if __name__ == '__main__':
    # Se ejecuta en el puerto 80 dentro del contenedor, como especificaste
    app.run(host='0.0.0.0', port=81, debug=False)