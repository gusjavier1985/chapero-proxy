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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json"
    }

    try:
        # Cargar página inicial para obtener cookies de sesión
        init_resp = session.get(f"{EMOVA_BASE}/ce/", headers=headers, timeout=10)
        
        payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
        
        # Probamos consultar endpoints comunes de datos o el estado directo
        endpoints_datos = [
            f"{EMOVA_BASE}/ce/api/lineaB/posiciones",
            f"{EMOVA_BASE}/ce/api/posiciones",
            f"{EMOVA_BASE}/api/lineaB/posiciones"
        ]

        resultados = {}
        for url in endpoints_datos:
            res = session.get(url, headers=headers, timeout=5)
            # Guardamos los primeros 200 caracteres de cada respuesta
            resultados[url] = {
                "status_code": res.status_code,
                "content_type": res.headers.get('Content-Type', ''),
                "body_snippet": res.text[:200]
            }

        return jsonify({
            "init_status": init_resp.status_code,
            "session_cookies": list(session.cookies.keys()),
            "respuestas_endpoints": resultados
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
