import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Habilitamos CORS para que Base44 pueda realizar consultas directamente desde el navegador
CORS(app)

EMOVA_USER = os.environ.get("EMOVA_USER", "")
EMOVA_PASS = os.environ.get("EMOVA_PASS", "")
EMOVA_BASE = "https://chapero.emova.com.ar"

def obtener_sesion_emova():
    session = requests.Session()
    login_url = f"{EMOVA_BASE}/api/login"
    payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Content-Type": "application/json"
    }
    try:
        resp = session.post(login_url, json=payload, headers=headers, timeout=10)
        if resp.status_code in [200, 201]:
            return session
    except Exception as e:
        print(f"Error autenticando en Emova: {e}")
    return None

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Chapero Línea B activa 🚆"})

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    session = obtener_sesion_emova()
    if not session:
        return jsonify({"error": "No se pudo autenticar con Emova"}), 500

    try:
        # Petición a la API interna del Chapero para obtener posiciones
        # (Ajustable según el endpoint exacto del Chapero)
        url_datos = f"{EMOVA_BASE}/api/lineaB/posiciones"
        resp = session.get(url_datos, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            return jsonify(data)
        else:
            # Respuesta de respaldo si el endpoint varía
            return jsonify(resp.json() if resp.text else {"status": "ok"})
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
