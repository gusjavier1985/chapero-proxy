import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_USER = os.environ.get("EMOVA_USER", "")
EMOVA_PASS = os.environ.get("EMOVA_PASS", "")
EMOVA_BASE = "https://chapero.emova.com.ar"

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Chapero Línea B activa 🚆"})

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
    
    # Rutas probables de la API de Emova
    endpoints_login = [
        f"{EMOVA_BASE}/ce/api/login",
        f"{EMOVA_BASE}/ce/login",
        f"{EMOVA_BASE}/api/login",
        f"{EMOVA_BASE}/ce/api/autenticar"
    ]
    
    ultimo_error = {}

    for login_url in endpoints_login:
        try:
            resp = session.post(login_url, json=payload, headers=headers, timeout=5)
            if resp.status_code in [200, 201]:
                # Si conecta exitosamente, intentamos traer los datos
                url_datos = f"{EMOVA_BASE}/ce/api/lineaB/posiciones"
                resp_datos = session.get(url_datos, headers=headers, timeout=5)
                if resp_datos.status_code == 200:
                    return jsonify(resp_datos.json())
                else:
                    return jsonify({
                        "login_exitoso_en": login_url,
                        "status_datos": resp_datos.status_code,
                        "respuesta": resp_datos.text
                    })
            else:
                ultimo_error[login_url] = f"Status: {resp.status_code}"
        except Exception as e:
            ultimo_error[login_url] = str(e)

    return jsonify({
        "error": "No se pudo encontrar la ruta de login válida",
        "intentos": ultimo_error
    }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
