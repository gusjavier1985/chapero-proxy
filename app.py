import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

HTML_TABLERO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tablero Línea B - Te Subo</title>
    <style>
        * { box-sizing: border-box; }
        body {
            background-color: #0d131f;
            color: #ffffff;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            margin: 0;
            padding: 12px;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #182232;
            padding: 12px 16px;
            border-radius: 8px;
            border-left: 4px solid #ef4444;
            margin-bottom: 16px;
        }
        .title { font-weight: bold; font-size: 1.1rem; color: #f1f5f9; }
        .badge { background: #22c55e; color: #000; font-weight: bold; padding: 4px 10px; border-radius: 20px; font-size: 0.75rem; }
        .section-header {
            font-size: 0.85rem;
            font-weight: bold;
            color: #94a3b8;
            text-transform: uppercase;
            margin: 16px 0 8px 4px;
            letter-spacing: 0.5px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(130px, 1fr));
            gap: 10px;
        }
        .card {
            background: #182232;
            border: 1px solid #2a374a;
            border-radius: 8px;
            padding: 10px;
            text-align: center;
        }
        .card.active {
            border-color: #22c55e;
            background: rgba(34, 197, 94, 0.1);
        }
        .train-id { font-size: 1.1rem; font-weight: bold; color: #38bdf8; }
        .train-dest { font-size: 0.75rem; color: #94a3b8; margin-top: 4px; }
        .empty { color: #64748b; font-size: 0.85rem; padding: 12px; text-align: center; grid-column: 1 / -1; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">CHAPERO LÍNEA B 🚆</div>
        <div id="badge" class="badge">EN VIVO</div>
    </div>

    <div class="section-header">Formaciones en Servicio / Maniobras</div>
    <div id="grid" class="grid">
        <div class="empty">Cargando formaciones...</div>
    </div>

    <script>
        async function cargarTablero() {
            try {
                const res = await fetch('/api/posiciones-linea-b');
                const data = await res.json();
                const grid = document.getElementById('grid');
                
                if (data.formaciones && data.formaciones.length > 0) {
                    grid.innerHTML = data.formaciones.map(f => `
                        <div class="card active">
                            <div class="train-id">${f.formacion}</div>
                            <div class="train-dest">${f.destino || 'LÍNEA B'}</div>
                        </div>
                    `).join('');
                } else {
                    grid.innerHTML = '<div class="empty">Sin formaciones registradas en este momento</div>';
                }
            } catch (e) {
                document.getElementById('badge').innerText = 'ERROR';
                document.getElementById('badge').style.background = '#ef4444';
            }
        }

        cargarTablero();
        setInterval(cargarTablero, 5000); // Sincronización automática cada 5 segundos
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/tablero')
def tablero_view():
    return render_template_string(HTML_TABLERO)

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    raw_token = os.environ.get("AUTH_TOKEN", "")
    auth_token = raw_token.strip().strip("'").strip('"').replace('\n', '').replace('\r', '')

    headers = {
        "x-auth-token": auth_token,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Origin": EMOVA_BASE,
        "Content-Type": "application/json",
        "Referer": f"{EMOVA_BASE}/ce/#/lineaB"
    }

    req_data = {}
    try:
        r = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        if r.status_code == 200:
            req_data = r.json()
    except Exception:
        pass

    hoy = datetime.now()
    inicio_str = (hoy - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
    fin_str = hoy.strftime("%Y-%m-%d 23:59:59")

    formaciones_encontradas = []
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
            "query": "query Maniobras($filter: ManiobrasFilterInput) {\n  maniobras(filter:$filter) {\n    idManiobra\n    linea\n    formacion\n    destino\n    estado\n  }\n}"
        }
        
        resp = requests.post(f"{EMOVA_BASE}/graphql", json=query_payload, headers=gql_headers, timeout=6)
        if resp.status_code == 200:
            raw_json = resp.json() or {}
            maniobras = (raw_json.get("data") or {}).get("maniobras") or []
            for m in maniobras:
                if isinstance(m, dict) and m.get("formacion"):
                    formaciones_encontradas.append({
                        "formacion": m.get("formacion"),
                        "destino": m.get("destino", ""),
                        "estado": m.get("estado", "CONFIRMADA")
                    })
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "requerimientos": req_data,
        "formaciones": formaciones_encontradas
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
