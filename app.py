import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Permitir CORS desde cualquier origen para que Base44 no tenga bloqueos
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzEzLCJ1c2VybmFtZSI6Im1tZW50YSIsImxpbmVhcyI6IkIiLCJhcmVhIjoiVHJhZmljbyIsInBlcm1pc29zIjpbInRyYWZpY28iLCJ0YWxsZXIiLCJGVCIsIm5jIl0sImlhdCI6MTc5MjI1MTg5MSwiZXhwIjoxNzkyMjczNDkxfQ.fiFrGmDPoXuhLz_Tal-4GT0lZYNe7v4Y_o084y4rKEQ"

@app.route('/')
def home():
    return jsonify({
        "status": "ok",
        "message": "API Proxy Chapero Línea B activa 🚆"
    })

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    headers = {
        "x-auth-token": AUTH_TOKEN,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Origin": EMOVA_BASE,
        "Content-Type": "application/json"
    }

    # 1. Obtener requerimientos del día
    requerimientos_data = {"servicio": 9, "requeridos": 9, "disponibles": 18}
    try:
        req_resp = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        if req_resp.status_code == 200:
            requerimientos_data = req_resp.json()
    except Exception:
        pass

    # 2. Obtener maniobras GraphQL
    maniobras_linea_b = []
    try:
        gql_headers = {
            **headers,
            "Accept": "application/graphql-response+json,application/json;q=0.9",
            "x-client-app": "sgf-frontend",
            "x-client-version": "7.52.0"
        }
        query_payload = {
            "operationName": "Maniobras",
            "variables": {"filter": {"inicio": "2026-10-10 00:00:00", "fin": "2026-10-17 23:59:59"}},
            "extensions": {"clientLibrary": {"name": "@apollo/client", "version": "4.2.9"}},
            "query": "query Maniobras($filter: ManiobrasFilterInput) {\n  maniobras(filter: $filter) {\n    idManiobra\n    linea\n    formacion\n    destino\n    boleta\n    fechaApertura\n    fechaCierre\n    usuarioApertura\n    usuarioCierre\n    comentarioApertura\n    comentarioCierre\n    estado\n    __typename\n  }\n}"
        }
        gql_resp = requests.post(f"{EMOVA_BASE}/graphql", json=query_payload, headers=gql_headers, timeout=5)
        if gql_resp.status_code == 200:
            datos_raw = gql_resp.json()
            maniobras = datos_raw.get("data", {}).get("maniobras", [])
            maniobras_linea_b = [m for m in maniobras if m.get("linea") == "B"]
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "linea": "B",
        "requerimientos": requerimientos_data,
        "total_maniobras_b": len(maniobras_linea_b),
        "maniobras": maniobras_linea_b
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
