import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"
# Token activo recién capturado desde la sesión de Chapero
AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzEzLCJ1c2VybmFtZSI6Im1tZW50YSIsImxpbmVhcyI6IkIiLCJhcmVhIjoiVHJhZmljbyIsInBlcm1pc29zIjpbInRyYWZpY28iLCJ0YWxsZXIiLCJGVCIsIm5jIl0sImlhdCI6MTc5MjM0Nzg4OCwiZXhwIjoxNzkyMzY5NDg4fQ.LSOoXw-tEJAxGj_Zi0RegQ07KH7y-zK12DlMtoPkSVk")

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    headers = {
        "x-auth-token": AUTH_TOKEN,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Origin": EMOVA_BASE,
        "Content-Type": "application/json"
    }

    # 1. Requerimientos
    req_data = {}
    try:
        r = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        if r.status_code == 200:
            req_data = r.json()
    except Exception:
        pass

    # 2. GraphQL Maniobras con Token Activo
    hoy = datetime.now()
    inicio_str = (hoy - timedelta(days=5)).strftime("%Y-%m-%d 00:00:00")
    fin_str = (hoy + timedelta(days=2)).strftime("%Y-%m-%d 23:59:59")

    raw_response = None
    formaciones_encontradas = []
    gql_status = None

    try:
        gql_headers = {
            **headers,
            "Accept": "application/graphql-response+json,application/json;q=0.9",
            "x-client-app": "sgf-frontend",
            "x-client-version": "7.52.0"
        }
        query_payload = {
            "operationName": "Maniobras",
            "variables": {"filter": {"inicio": inicio_str, "fin": fin_str}},
            "extensions": {"clientLibrary": {"name": "@apollo/client", "version": "4.2.9"}},
            "query": "query Maniobras($filter: ManiobrasFilterInput) {\n  maniobras(filter: $filter) {\n    idManiobra\n    linea\n    formacion\n    destino\n    estado\n    __typename\n  }\n}"
        }
        resp = requests.post(f"{EMOVA_BASE}/graphql", json=query_payload, headers=gql_headers, timeout=6)
        gql_status = resp.status_code
        
        if resp.status_code == 200:
            raw_json = resp.json() or {}
            raw_response = raw_json
            maniobras = (raw_json.get("data") or {}).get("maniobras") or []
            
            for m in maniobras:
                if isinstance(m, dict):
                    formaciones_encontradas.append({
                        "formacion": m.get("formacion", ""),
                        "destino": m.get("destino", ""),
                        "estado": m.get("estado", "CONFIRMADA"),
                        "linea": m.get("linea", "B")
                    })
        else:
            raw_response = resp.text
    except Exception as e:
        raw_response = str(e)

    return jsonify({
        "status": "success",
        "requerimientos": req_data,
        "formaciones": formaciones_encontradas,
        "debug_status": gql_status,
        "debug_raw": raw_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
