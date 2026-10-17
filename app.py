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
    
    # 1. Primero navegamos la página principal para levantar tokens/cookies iniciales
    try:
        session.get(f"{EMOVA_BASE}/ce/", headers=headers, timeout=5)
    except:
        pass

    payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
    
    # Probamos las variantes sobre el endpoint validado /ce/
    urls_test = [
        f"{EMOVA_BASE}/ce/api/login",
        f"{EMOVA_BASE}/ce/login",
        f"{EMOVA_BASE}/ce/api/autenticar"
    ]
    
    for login_url in urls_test:
        try:
            # Probamos en JSON
            resp = session.post(login_url, json=payload, headers=headers, timeout=5)
            if resp.status_code in [200, 201]:
                # Éxito: pedimos las posiciones
                resp_datos = session.get(f"{EMOVA_BASE}/ce/api/lineaB/posiciones", headers=headers, timeout=5)
                return jsonify(resp_datos.json() if resp_datos.status_code == 200 else {"status": "login_ok", "data_resp": resp_datos.text})
            
            # Si da 405, probamos enviando datos como formulario tradicional
            if resp.status_code == 405:
                resp_form = session.post(login_url, data=payload, timeout=5)
                if resp_form.status_code in [200, 201]:
                    resp_datos = session.get(f"{EMOVA_BASE}/ce/api/lineaB/posiciones", headers=headers, timeout=5)
                    return jsonify(resp_datos.json() if resp_datos.status_code == 200 else {"status": "login_ok", "data_resp": resp_datos.text})
        except Exception as e:
            pass

    # Si la API de la SPA no expone login directo, consultamos el estado directamente
    try:
        resp_directa = session.get(f"{EMOVA_BASE}/ce/api/lineaB/posiciones", headers=headers, timeout=5)
        if resp_directa.status_code == 200:
            return jsonify(resp_directa.json())
        return jsonify({"info": "Ruta /ce/ confirmada. Respuesta del servidor:", "status": resp_directa.status_code, "body": resp_directa.text[:300]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
