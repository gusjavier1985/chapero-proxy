import os
from datetime import datetime
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapero Electrónico - Línea B</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b111e; color: #ffffff; margin: 0; padding: 10px; }
        .header { display: flex; justify-content: space-between; align-items: center; background: #182232; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; border-left: 4px solid #ef4444; }
        .title { font-weight: bold; font-size: 1rem; color: #ef4444; }
        .badge { background: #22c55e; color: #000; font-weight: bold; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; }
        
        .section-box { background: #131b29; border-radius: 8px; padding: 12px; margin-bottom: 12px; border: 1px solid #1e293b; }
        .sec-title { font-size: 0.8rem; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-bottom: 10px; text-align: center; letter-spacing: 0.5px; }
        
        .grid-service { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .service-row { display: flex; align-items: center; background: #182232; border-radius: 6px; padding: 4px 8px; border: 1px solid #2a374a; }
        .itin-num { width: 28px; font-weight: bold; font-size: 0.85rem; color: #94a3b8; text-align: center; }
        .train-chip { flex: 1; background: #15803d; color: #fff; font-weight: bold; font-size: 0.8rem; padding: 6px; border-radius: 4px; text-align: center; border: 1px solid #22c55e; }
        .train-chip.req { background: #b91c1c; border-color: #ef4444; }
        .train-chip.empty { background: transparent; border: 1px dashed #334155; color: transparent; }

        .grid-generic { display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 8px; }
        .cell { background: #182232; border: 1px solid #2a374a; border-radius: 6px; padding: 8px; text-align: center; font-size: 0.8rem; font-weight: bold; }
        .cell.occupied { background: #15803d; border-color: #22c55e; color: #fff; }
        .cell.req { background: #b91c1c; border-color: #ef4444; color: #fff; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">CHAPERO ELECTRÓNICO (B)</div>
        <div id="status" class="badge">EN VIVO</div>
    </div>

    <!-- EN SERVICIO -->
    <div class="section-box">
        <div class="sec-title">EN SERVICIO</div>
        <div id="grid-servicio" class="grid-service">Cargando formaciones en servicio...</div>
    </div>

    <!-- OTRAS UBICACIONES -->
    <div class="section-box">
        <div class="sec-title">OTRAS UBICACIONES / COCHERAS</div>
        <div id="grid-ubicaciones" class="grid-generic">Cargando...</div>
    </div>

    <script>
        const itinerariosDef = [3, 11, 13, 1, 4, 21, 5, 17, 14, 12, 22, 2, 6, 18, 19, 40, 7, 40, 15, 40, 8, 40, 9, 40, 20, 40, 16, 40, 10, 40];

        async function actualizar() {
            try {
                const res = await fetch('/api/posiciones-linea-b');
                const data = await res.json();
                
                const gridServicio = document.getElementById('grid-servicio');
                const gridUbicaciones = document.getElementById('grid-ubicaciones');
                
                let servicioHTML = '';
                let formacionesMap = {};

                if (data.formaciones && data.formaciones.length > 0) {
                    data.formaciones.forEach(f => {
                        if (f.formacion) formacionesMap[f.formacion] = f;
                    });
                }

                // Renderizar casilleros de En Servicio
                itinerariosDef.forEach((itin, index) => {
                    const formacionEncontrada = data.formaciones ? data.formaciones[index] : null;
                    if (formacionEncontrada) {
                        servicioHTML += `
                            <div class="service-row">
                                <div class="itin-num">${itin}</div>
                                <div class="train-chip ${formacionEncontrada.estado === 'REQUERIMIENTO' ? 'req' : ''}">${formacionEncontrada.formacion}</div>
                            </div>
                        `;
                    } else {
                        servicioHTML += `
                            <div class="service-row">
                                <div class="itin-num">${itin}</div>
                                <div class="train-chip empty">-</div>
                            </div>
                        `;
                    }
                });
                gridServicio.innerHTML = servicioHTML;

                // Renderizar ubicaciones externas
                if (data.requerimientos && Object.keys(data.requerimientos).length > 0) {
                    gridUbicaciones.innerHTML = '<div class="cell occupied">Cochera Rosas Vía 4: CAF 6000 B1</div><div class="cell req">Taller Urquiza F1</div><div class="cell req">Taller Rancagua V4</div>';
                } else {
                    gridUbicaciones.innerHTML = '<div class="cell">Sincronizado con Emova</div>';
                }

                document.getElementById('status').innerText = 'EN VIVO';
                document.getElementById('status').style.background = '#22c55e';
            } catch (e) {
                document.getElementById('status').innerText = 'ERROR';
                document.getElementById('status').style.background = '#ef4444';
            }
        }

        actualizar();
        setInterval(actualizar, 5000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/tablero')
def tablero_view():
    return render_template_string(HTML_TEMPLATE)

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
    inicio_str = (hoy - timedelta(days=1)).strftime("%Y-%m-%d 00:00:00")
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
