import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzEzLCJ1c2VybmFtZSI6Im1tZW50YSIsImxpbmVhcyI6IkIiLCJhcmVhIjoiVHJhZmljbyIsInBlcm1pc29zIjpbInRyYWZpY28iLCJ0YWxsZXIiLCJGVCIsIm5jIl0sImlhdCI6MTc5MjI1MTg5MSwiZXhwIjoxNzkyMjczNDkxfQ.fiFrGmDPoXuhLz_Tal-4GT0lZYNe7v4Y_o084y4rKEQ"

COMMON_HEADERS = {
    "x-auth-token": AUTH_TOKEN,
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
    "Origin": EMOVA_BASE
}

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Chapero Línea B activa 🚆"})

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    try:
        # 1. Consultar Requerimientos del Día (Endpoint REST)
        req_url = f"{EMOVA_BASE}/api/ce/requerimientosDia"
        req_headers = {**COMMON_HEADERS, "Content-Type": "application/json"}
        req_resp = requests.get(req_url, headers=req_headers, timeout=10)
        
        requerimientos_data = req_resp.json() if req_resp.status_code == 200 else {}

        # 2. Consultar Maniobras (Endpoint GraphQL)
        gql_url = f"{EMOVA_BASE}/graphql"
        gql_headers = {**COMMON_HEADERS, "Accept": "application/graphql-response+json,application/json;q=0.9", "Content-Type": "application/json", "x-client-app": "sgf-frontend", "x-client-version": "7.52.0"}
        
        query_payload = {
            "operationName": "Maniobras",
            "variables": {"filter": {"inicio": "2026-10-10 00:00:00", "fin": "2026-10-17 23:59:59"}},
            "extensions": {"clientLibrary": {"name": "@apollo/client", "version": "4.2.9"}},
            "query": "query Maniobras($filter: ManiobrasFilterInput) {\n  maniobras(filter: $filter) {\n    idManiobra\n    linea\n    formacion\n    destino\n    boleta\n    fechaApertura\n    fechaCierre\n    usuarioApertura\n    usuarioCierre\n    comentarioApertura\n    comentarioCierre\n    estado\n    __typename\n  }\n}"
        }

        gql_resp = requests.post(gql_url, json=query_payload, headers=gql_headers, timeout=10)
        maniobras_linea_b = []
        
        if gql_resp.status_code == 200:
            datos_raw = gql_resp.json()
            maniobras = datos_raw.get("data", {}).get("maniobras", [])
            # Filtramos únicamente las maniobras de la Línea B
            maniobras_linea_b = [m for m in maniobras if m.get("linea") == "B"]

        return jsonify({
            "status": "success",
            "linea": "B",
            "requerimientos": requerimientos_data,
            "total_maniobras_b": len(maniobras_linea_b),
            "maniobras": maniobras_linea_b
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
