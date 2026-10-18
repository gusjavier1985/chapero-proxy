import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"
# Recomendación: idealmente usar os.environ.get("AUTH_TOKEN") si configurás la variable de entorno en Render
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

    # 1. Requerimientos del día
    requerimientos_data = {"servicio": 10, "requeridos": 9, "disponibles": 18}
    req_error = None
    try:
        req_resp = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        if req_resp.status_code == 200:
            requerimientos_data = req_resp.json()
        else:
            req_error = f"HTTP {req_resp.status_code}"
    except Exception as e:
        req_error = str(e)

    # 2. Consultar GraphQL de maniobras
    hoy = datetime.now()
    inicio_str = (hoy - timedelta(days=5)).strftime("%Y-%m-%d 00:00:00")
    fin_str = (hoy + timedelta(days=1)).strftime("%Y-%m-%d 23:59:59")

    formaciones_activas = []
    graphql_error = None
    raw_response_snippet = None

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
        gql_resp = requests.post(f"{EMOVA_BASE}/graphql", json=query_payload, headers=gql_headers, timeout=5)
        raw_response_snippet = gql_resp.text[:300] # Para diagnóstico
        
        if gql_resp.status_code == 200:
            datos_raw = gql_resp.json()
            maniobras = datos_raw.get("data", {}).get("maniobras", [])
            for m in maniobras:
                if m.get("linea") == "B" and m.get("formacion"):
                    formaciones_activas.append({
                        "formacion": m.get("formacion"),
                        "destino": m.get("destino", ""),
                        "estado": m.get("estado", "CONFIRMADA")
                    })
        else:
            graphql_error = f"GraphQL HTTP {gql_resp.status_code}"
    except Exception as e:
        graphql_error = str(e)

    return jsonify({
        "status": "success" if not graphql_error else "error_graphql",
        "linea": "B",
        "requerimientos": requerimientos_data,
        "formaciones": formaciones_activas,
        "diagnostico": {
            "graphql_error": graphql_error,
            "req_error": req_error,
            "raw_snippet": raw_response_snippet
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
