import os
from datetime import datetime, timedelta
import requests
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

HTML_FICHERO_COMPLETO = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fichero - Línea B</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b111e; color: #fff; margin: 0; padding: 10px; }
        .header { display: flex; justify-content: space-between; align-items: center; background: #162032; padding: 10px 14px; border-radius: 8px; margin-bottom: 12px; }
        .badge { background: #10b981; color: #000; font-weight: bold; padding: 3px 8px; border-radius: 12px; font-size: 0.75rem; }
        
        .section-box { background: #162032; border-radius: 8px; padding: 12px; margin-bottom: 12px; border: 1px solid #233248; }
        .sec-title { font-size: 0.8rem; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-bottom: 10px; text-align: center; letter-spacing: 0.5px; }
        
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
        .grid-4 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
        .grid-list { display: flex; flex-direction: column; gap: 6px; }

        .cell { background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 8px; min-height: 42px; display: flex; align-items: center; justify-content: center; font-size: 0.8rem; text-align: center; font-weight: bold; }
        .cell.occupied { background: #15803d; border-color: #22c55e; color: #fff; }
        .cell.req { background: #b91c1c; border-color: #ef4444; color: #fff; }
        
        .track-num { font-size: 0.7rem; color: #64748b; margin-right: 6px; }
    </style>
</head>
<body>
    <div class="header">
        <span style="font-weight:bold; color:#ef4444;">CHAPERO LÍNEA B 🚆</span>
        <span id="sync" class="badge">Sincronizado</span>
    </div>

    <!-- COCHERA ROSAS -->
    <div class="section-box">
        <div class="sec-title">COCHERA ROSAS</div>
        <div class="grid-2">
            <div class="cell occupied">MITSUBISHI N</div>
            <div class="cell occupied">CAF 6000 A1</div>
            <div class="cell occupied">MITSUBISHI P</div>
            <div class="cell occupied">MITSUBISHI L</div>
            <div class="cell occupied">MITSUBISHI G</div>
            <div class="cell req">MITSUBISHI A</div>
            <div class="cell occupied">MITSUBISHI K</div>
            <div class="cell occupied">CAF 6000 I1</div>
        </div>
    </div>

    <!-- ANDEN ROSAS -->
    <div class="section-box">
        <div class="sec-title">ANDÉN ROSAS</div>
        <div class="grid-2">
            <div class="cell occupied"><span class="track-num">S</span> MITSUBISHI O</div>
            <div class="cell occupied"><span class="track-num">N</span> CAF 6000 F1</div>
        </div>
    </div>

    <!-- TALLER URQUIZA -->
    <div class="section-box">
        <div class="sec-title">TALLER URQUIZA</div>
        <div class="grid-list">
            <div class="cell occupied"><span class="track-num">F1</span> CAF 6000 H1</div>
            <div class="cell occupied"><span class="track-num">F2</span> CAF 6000 B1</div>
        </div>
    </div>

    <!-- ECHEVERRÍA -->
    <div class="section-box">
        <div class="sec-title">ECHEVERRÍA</div>
        <div class="grid-2">
            <div class="cell occupied"><span class="track-num">N</span> CAF 6000 M1</div>
            <div class="cell occupied"><span class="track-num">N</span> CAF 6000 R1</div>
        </div>
    </div>

    <!-- TALLER RANCAGUA -->
    <div class="section-box">
        <div class="sec-title">TALLER RANCAGUA</div>
        <div class="grid-list">
            <div class="cell occupied"><span class="track-num">V4</span> MITSUBISHI I</div>
            <div class="cell occupied"><span class="track-num">V6</span> MITSUBISHI Q</div>
            <div class="cell occupied"><span class="track-num">V7</span> MITSUBISHI D</div>
            <div class="cell req"><span class="track-num">V9</span> MITSUBISHI E</div>
            <div class="cell occupied"><span class="track-num">V10</span> MITSUBISHI T</div>
        </div>
    </div>

    <script>
        async function refrescar() {
            try {
                await fetch('/api/posiciones-linea-b');
                document.getElementById('sync').innerText = 'EN VIVO';
                document.getElementById('sync').style.background = '#10b981';
            } catch(e) {
                document.getElementById('sync').innerText = 'ERROR';
                document.getElementById('sync').style.background = '#ef4444';
            }
        }
        setInterval(refrescar, 10000);
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/tablero')
def tablero_view():
    return render_template_string(HTML_FICHERO_COMPLETO)

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
