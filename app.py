import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
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

    # 1. Requerimientos
    requerimientos_data = {
        "servicio": 10,
        "requeridos": 9,
        "disponibles": 18
    }
    try:
        req_resp = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        if req_resp.status_code == 200:
            requerimientos_data = req_resp.json()
    except Exception:
        pass

    # 2. Obtener Maniobras de GraphQL
    formaciones_lista = []
    maniobras_raw = []
    
    # Rango amplio para asegurar capturar formaciones vigentes
    hoy = datetime.now()
    inicio_str = (hoy - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    fin_str = (hoy + timedelta(days=2)).strftime("%Y-%m-%d 23:59:59")

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
        if gql_resp.status_code == 200:
            datos_json = gql_resp.json()
            maniobras_raw = datos_json.get("data", {}).get("maniobras", [])
            
            # Extraer de forma directa sin filtros restrictivos
            for m in maniobras_raw:
                # Tomamos todas las de Línea B o las que tengan formación válida
                linea = str(m.get("linea", "")).upper()
                formacion = m.get("formacion")
                destino = m.get("destino", "")
                
                if (linea == "B" or not linea) and formacion:
                    formaciones_lista.append({
                        "formacion": formacion,
                        "destino": destino,
                        "estado": m.get("estado", "CONFIRMADA"),
                        "linea": "B"
                    })
    except Exception as e:
        print("Error al consultar GraphQL:", e)

    # Garantía de devolución: si la extracción quedó vacía por cualquier fallo de red de Emova,
    # armamos la lista directa desde maniobras_raw si existe
    if not formaciones_lista and maniobras_raw:
        for m in maniobras_raw:
            if m.get("formacion"):
                formaciones_lista.append({
                    "formacion": m.get("formacion"),
                    "destino": m.get("destino", ""),
                    "estado": m.get("estado", "CONFIRMADA"),
                    "linea": "B"
                })

    return jsonify({
        "status": "success",
        "linea": "B",
        "requerimientos": requerimientos_data,
        "formaciones": formaciones_lista,
        "total_formaciones": len(formaciones_lista)
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
