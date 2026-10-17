import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"
# Token extraído directamente de la inspección de red
AUTH_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MzEzLCJ1c2VybmFtZSI6Im1tZW50YSIsImxpbmVhcyI6IkIiLCJhcmVhIjoiVHJhZmljbyIsInBlcm1pc29zIjpbInRyYWZpY28iLCJ0YWxsZXIiLCJGVCIsIm5jIl0sImlhdCI6MTc5MjI1MTg5MSwiZXhwIjoxNzkyMjczNDkxfQ.fiFrGmDPoXuhLz_Tal-4GT0lZYNe7v4Y_o084y4rKEQ"

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Chapero GraphQL Línea B activa 🚆"})

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    url_graphql = f"{EMOVA_BASE}/graphql"
    
    headers = {
        "Accept": "application/graphql-response+json,application/json;q=0.9",
        "Content-Type": "application/json",
        "x-client-app": "sgf-frontend",
        "x-client-version": "7.52.0",
        "x-auth-token": AUTH_TOKEN,
        "Origin": EMOVA_BASE,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    # Query GraphQL de Maniobras extraída de Eruda
    query_payload = {
        "operationName": "Maniobras",
        "variables": {
            "filter": {
                "inicio": "2026-10-10 00:00:00",
                "fin": "2026-10-17 23:59:59"
            }
        },
        "extensions": {
            "clientLibrary": {
                "name": "@apollo/client",
                "version": "4.2.9"
            }
        },
        "query": """query Maniobras($filter: ManiobrasFilterInput) {
  maniobras(filter: $filter) {
    idManiobra
    linea
    formacion
    destino
    boleta
    fechaApertura
    fechaCierre
    usuarioApertura
    usuarioCierre
    comentarioApertura
    comentarioCierre
    estado
    __typename
  }
}"""
    }

    try:
        response = requests.post(url_graphql, json=query_payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            datos_raw = response.json()
            maniobras = datos_raw.get("data", {}).get("maniobras", [])
            
            # Filtramos únicamente las maniobras de la Línea B
            maniobras_linea_b = [m for m in maniobras if m.get("linea") == "B"]
            
            return jsonify({
                "status": "success",
                "linea": "B",
                "total_maniobras_b": len(maniobras_linea_b),
                "data": maniobras_linea_b
            })
        else:
            return jsonify({
                "error": "Error de comunicación con GraphQL",
                "status_code": response.status_code,
                "raw_response": response.text
            }), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
