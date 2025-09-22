import os
from flask import Flask, request, jsonify

app = Flask(__name__)

# Lee el token de verificación desde una variable de entorno por seguridad.
# Debes configurar esta variable en Google Cloud Run.
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    # Lógica para la verificación del webhook de Meta
    # Meta envía una petición GET para validar que el servidor es el correcto
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if mode and token:
        # Verifica que el token de la petición coincida con tu VERIFY_TOKEN
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            print("Webhook verificado con éxito.")
            return challenge, 200
        else:
            return "Verificación de token fallida", 403
    return "Error en la petición de verificación", 400

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    # Lógica para manejar las notificaciones de eventos (mensajes, estados, etc.)
    data = request.json
    print("¡Webhook recibido!")
    print("Datos:", data)

    # Puedes agregar tu lógica aquí para procesar los datos
    # Por ejemplo, para responder a un mensaje entrante

    return jsonify({"message": "Evento recibido"}), 200

if __name__ == '__main__':
    # Configura el servidor para escuchar en el puerto requerido por Google Cloud Run
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)