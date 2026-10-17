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
    login_url = f"{EMOVA_BASE}/api/login"
    payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json"
    }
    
    try:
        # Intentamos el login
        resp = session.post(login_url, json=payload, headers=headers, timeout=10)
        
        # Si Emova rechaza el login, devolvemos el detalle para diagnosticar
        if resp.status_code not in [200, 201]:
            return jsonify({
                "error": "Rechazado por Emova",
                "status_code": resp.status_code,
                "respuesta_emova": resp.text
            }), 500

        # Si el login fue exitoso, consultamos los datos de la Línea B
        url_datos = f"{EMOVA_BASE}/api/lineaB/posiciones"
        resp_datos = session.get(url_datos, timeout=10)
        
        if resp_datos.status_code == 200:
            return jsonify(resp_datos.json())
        else:
            return jsonify({"status": "login_ok", "datos_status": resp_datos.status_code, "raw": resp_datos.text})
            
    except Exception as e:
        return jsonify({"error_excepcion": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
