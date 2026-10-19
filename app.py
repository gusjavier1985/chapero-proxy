import os
from datetime import datetime, timedelta
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

        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .grid-3 { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; }
        .cell { background: #182232; border: 1px solid #2a374a; border-radius: 6px; padding: 8px; text-align: center; font-size: 0.8rem; font-weight: bold; }
        .cell.occupied { background: #15803d; border-color: #22c55e; color: #fff; }
        .cell.req { background: #b91c1c; border-color: #ef4444; color: #fff; }
        .track-num { font-size: 0.7rem; color: #64748b; margin-right: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="title">CHAPERO ELECTRÓNICO (B) 🚆</div>
        <div id="status" class="badge">EN VIVO</div>
    </div>

    <!-- EN SERVICIO -->
    <div class="section-box">
        <div class="sec-title">EN SERVICIO</div>
        <div id="grid-servicio" class="grid-service">Cargando formaciones...</div>
    </div>

    <!-- COCHERA ROSAS -->
    <div class="section-box">
        <div class="sec-title">COCHERA ROSAS</div>
        <div class="grid-3">
            <div class="cell"><span class="track-num">1</span></div>
            <div class="cell"><span class="track-num">1</span></div>
            <div class="cell"><span class="track-num">1</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="cell occupied"><span class="track-num">4</span> CAF 6000 B1</div>
            <div class="cell"><span class="track-num">4</span></div>
            <div class="cell"><span class="track-num">4</span></div>
        </div>
    </div>

    <!-- TALLER URQUIZA -->
    <div class="section-box">
        <div class="sec-title">TALLER URQUIZA</div>
        <div class="grid-2">
            <div class="cell req"><span class="track-num">F1</span> CAF 6000 F1</div>
            <div class="cell req"><span class="track-num">F2</span> CAF 6000 H1</div>
        </div>
    </div>

    <!-- TALLER RANCAGUA -->
    <div class="section-box">
        <div class="sec-title">TALLER RANCAGUA</div>
        <div class="grid-2">
            <div class="cell req"><span class="track-num">V4</span> MITSUBISHI A</div>
            <div class="cell req"><span class="track-num">V5</span> MITSUBISHI C</div>
        </div>
    </div>

    <!-- LYNCH & TJC -->
    <div class="section-box">
        <div class="sec-title">LYNCH / TJC</div>
        <div class="grid-3">
            <div class="cell req">CAF 6000 D1</div>
            <div class="cell req">CAF 6000 C1</div>
            <div class="cell req">CAF 6000 L1</div>
        </div>
    </div>

    <script>
        const itinerariosDef = [
            {n: 3, f: 'MITSUBISHI H'}, {n: 11, f: 'MITSUBISHI K'},
            {n: 13, f: 'MITSUBISHI L'}, {n: 1, f: 'CAF 6000 H1'},
            {n: 4, f: 'MITSUBISHI O'}, {n: 21, f: ''},
            {n: 5, f: 'MITSUBISHI N'}, {n: 17, f: 'MITSUBISHI Q'},
            {n: 14, f: 'CAF 6000 I1'}, {n: 12, f: 'CAF 6000 K1'},
            {n: 22, f: ''}, {n: 2, f: 'MITSUBISHI I'},
            {n: 6, f: 'MITSUBISHI O'}, {n: 18, f: 'MITSUBISHI P'},
            {n: 19, f: 'MITSUBISHI G'}, {n: 40, f: ''},
            {n: 7, f: 'CAF 6000 E1'}, {n: 40, f: ''},
            {n: 15, f: 'MITSUBISHI D'}, {n: 40, f: ''},
            {n: 8, f: 'MITSUBISHI T'}, {n: 40, f: ''},
            {n: 9, f: 'CAF 6000 M1'}, {n: 40, f: ''},
            {n: 20, f: 'CAF 6000 J1'}, {n: 40, f: ''},
            {n: 16, f: 'CAF 6000 G1'}, {n: 40, f: ''},
            {n: 10, f: 'MITSUBISHI M'}, {n: 40, f: ''}
        ];

        async function actualizar() {
            try {
                const res = await fetch('/api/posiciones-linea-b');
                const data = await res.json();

                let servicioHTML = '';
                
                itinerariosDef.forEach(item => {
                    if (item.f) {
                        servicioHTML += `
                            <div class="service-row">
                                <div class="itin-num">${item.n}</div>
                                <div class="train-chip">${item.f}</div>
                            </div>
                        `;
                    } else {
                        servicioHTML += `
                            <div class="service-row">
                                <div class="itin-num">${item.n}</div>
                                <div class="train-chip empty">-</div>
                            </div>
                        `;
                    }
                });

                document.getElementById('grid-servicio').innerHTML = servicioHTML;
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

    try:
        r = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        return jsonify({"status": "success", "data": r.json() if r.status_code == 200 else {}})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
