# Importa la biblioteca requests
import requests
import os

from flask import Flask, request, jsonify

app = Flask(__name__)

# Lee el token de verificación del entorno (Cloud Run)
VERIFY_TOKEN = os.environ.get('VERIFY_TOKEN')
WHATSAPP_API_TOKEN = os.environ.get('WHATSAPP_API_TOKEN')

@app.route("/webhook", methods=["GET"])
def verify():
    # Código para verificar el token...
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("Webhook verificado con éxito.")
            return challenge, 200
        else:
            return "Verificación de token fallida.", 403
    return "Error de verificación.", 400


@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.get_json()
    print("Datos recibidos:", data)

    if data.get('object') == 'whatsapp_business_account':
        try:
            for entry in data['entry']:
                for change in entry['changes']:
                    if change['field'] == 'messages':
                        message_data = change['value']['messages'][0]
                        # Extrae la información del mensaje
                        phone_number_id = change['value']['metadata']['phone_number_id']
                        from_number = message_data['from']
                        text_body = message_data['text']['body']
                        
                        # Responde al mensaje
                        send_whatsapp_message(
                            to=from_number,
                            message=f"Recibí tu mensaje: '{text_body}'",
                            phone_number_id=phone_number_id
                        )

        except (KeyError, IndexError) as e:
            print(f"Error al procesar el mensaje: {e}")
            return "Error al procesar el mensaje", 400

    return jsonify({"status": "ok"}), 200

def send_whatsapp_message(to, message, phone_number_id):
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {
            "body": message
        }
    }

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"
    
    response = requests.post(url, headers=headers, json=data)
    
    print("Respuesta de la API de WhatsApp:", response.json())
    return response.json()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
