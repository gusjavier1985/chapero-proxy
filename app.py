import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

# Toma automáticamente el usuario y contraseña que ya configuraste en Render
EMOVA_USER = os.environ.get("EMOVA_USER")
EMOVA_PASS = os.environ.get("EMOVA_PASS")

# Caché global del token en memoria
CACHED_TOKEN = os.environ.get("AUTH_TOKEN")

def obtener_token_valido():
    """Realiza login automático en Emova para obtener un x-auth-token fresco."""
    global CACHED_TOKEN
    login_url = f"{EMOVA_BASE}/api/auth/login"
    payload = {
        "username": EMOVA_USER,
        "password": EMOVA_PASS
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36"
    }

    try:
        resp = requests.post(login_url, json=payload, headers=headers, timeout=5)
        if resp.status_code == 200:
            token = resp.headers.get("x-auth-token")
            if not token and isinstance(resp.json(), dict):
                token = resp.json().get("token") or resp.json().get("x-auth-token")
            
            if token:
                CACHED_TOKEN = token
                return token
    except Exception as e:
        print(f"Error en auto-login: {e}")
    
    return CACHED_TOKEN

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy con Auto-Login Activa 🚆"})

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    global CACHED_TOKEN

    if not CACHED_TOKEN:
        CACHED_TOKEN = obtener_token_valido()

    headers = {
        "x-auth-token": CACHED_TOKEN,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Origin": EMOVA_BASE,
        "Content-Type": "application/json",
        "Referer": f"{EMOVA_BASE}/ce/#/lineaB"
    }

    # 1. Requerimientos
    req_data = {}
    try:
        r = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        if r.status_code == 200 and "error" not in r.text.lower():
            req_data = r.json()
    except Exception:
        pass

    # 2. Consulta GraphQL con re-intento automático por expiración
    hoy = datetime.now()
    inicio_str = (hoy - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    fin_str = hoy.strftime("%Y-%m-%d 23:59:59")

    query_payload = {
        "operationName": "Maniobras",
        "variables": {"filter": {"inicio": inicio_str, "fin": fin_str}},
        "extensions": {"clientLibrary": {"name": "@apollo/client", "version": "4.2.9"}},
        "query": "query Maniobras($filter: ManiobrasFilterInput) {\n  maniobras(filter: $filter) {\n    idManiobra\n    linea\n    formacion\n    destino\n    boleta\n    fechaApertura\n    fechaCierre\n    usuarioApertura\n    usuarioCierre\n    comentarioApertura\n    comentarioCierre\n    estado\n    __typename\n  }\n}"
    }

    gql_headers = {
        **headers,
        "Accept": "application/graphql-response+json,application/json;q=0.9",
        "x-client-app": "sgf-frontend",
        "x-client-version": "7.52.0"
    }

    resp = None
    try:
        resp = requests.post(f"{EMOVA_BASE}/graphql", json=query_payload, headers=gql_headers, timeout=6)
        
        # Si la sesión expiró, ejecuta auto-login y reintenta al instante
        if resp.status_code in [401, 403] or (resp.status_code == 200 and "expirada" in resp.text.lower()):
            nuevo_token = obtener_token_valido()
            if nuevo_token:
                gql_headers["x-auth-token"] = nuevo_token
                resp = requests.post(f"{EMOVA_BASE}/graphql", json=query_payload, headers=gql_headers, timeout=6)
    except Exception as e:
        pass

    formaciones_encontradas = []
    raw_response = None
    gql_status = resp.status_code if resp else None

    if resp and resp.status_code == 200:
        raw_json = resp.json() or {}
        raw_response = raw_json
        maniobras = (raw_json.get("data") or {}).get("maniobras") or []
        if isinstance(maniobras, list):
            for m in maniobras:
                if isinstance(m, dict):
                    formacion = m.get("formacion")
                    linea = str(m.get("linea", "")).upper()
                    if formacion and (linea == "B" or not linea):
                        formaciones_encontradas.append({
                            "idManiobra": m.get("idManiobra"),
                            "formacion": formacion,
                            "destino": m.get("destino", ""),
                            "estado": m.get("estado", "CONFIRMADA")
                        })

    return jsonify({
        "status": "success",
        "requerimientos": req_data,
        "formaciones": formaciones_encontradas,
        "debug_status": gql_status,
        "debug_raw": raw_response
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
