import os
import requests
from flask import Flask, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

HTML_BASE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="10">
    <title>Chapero Electrónico - Línea B</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0b111e; color: #ffffff; margin: 0; padding: 8px; font-size: 12px; }
        
        .top-bar { display: flex; align-items: center; justify-content: space-between; background: #162032; padding: 10px; border-radius: 8px; margin-bottom: 10px; border: 1px solid #233248; }
        .line-badge { background: #ef4444; color: #fff; font-weight: bold; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 1.1rem; }
        .stats-group { display: flex; gap: 8px; text-align: center; }
        .stat-box { background: #1e293b; padding: 4px 8px; border-radius: 6px; border: 1px solid #2a374a; }
        .stat-val { font-weight: bold; font-size: 0.95rem; color: #fff; }
        .stat-lbl { font-size: 0.6rem; color: #94a3b8; text-transform: uppercase; }

        .timer-bar { display: flex; align-items: center; background: #162032; padding: 8px 12px; border-radius: 8px; margin-bottom: 12px; gap: 10px; border: 1px solid #233248; }
        .timer-clock { font-size: 1.1rem; }
        .timer-text { font-weight: bold; font-size: 0.85rem; color: #38bdf8; }

        .section-box { background: #131b29; border-radius: 8px; padding: 10px; margin-bottom: 10px; border: 1px solid #1e293b; }
        .sec-title { font-size: 0.75rem; font-weight: bold; color: #94a3b8; text-transform: uppercase; margin-bottom: 8px; text-align: center; letter-spacing: 0.5px; }
        
        .grid-service { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        .service-row { display: flex; align-items: center; background: #182232; border-radius: 5px; padding: 3px 6px; border: 1px solid #2a374a; }
        .itin-num { width: 24px; font-weight: bold; font-size: 0.8rem; color: #cbd5e1; text-align: center; }
        
        .train-chip { flex: 1; font-weight: bold; font-size: 0.75rem; padding: 5px; border-radius: 4px; text-align: center; border: 1px solid transparent; display: flex; align-items: center; justify-content: center; }
        .train-chip.empty { background: #182232; border: 1px dashed #2a374a; color: #475569; }
        .train-chip.green { background: #15803d; border-color: #22c55e; color: #fff; }
        .train-chip.red { background: #b91c1c; border-color: #ef4444; color: #fff; }
        .train-chip.black { background: #18181b; border-color: #3f3f46; color: #fff; }
        .train-chip.maroon { background: #581c87; border-color: #7e22ce; color: #e9d5ff; }
        .train-chip.striped { background: repeating-linear-gradient(45deg, #854d0e, #854d0e 10px, #713f12 10px, #713f12 20px); border-color: #a16207; color: #fff; font-size: 0.7rem; }

        .track-prefix { font-size: 0.75rem; color: #e2e8f0; font-weight: 800; margin-right: 6px; opacity: 0.9; }

        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        .grid-1 { display: grid; grid-template-columns: 1fr; gap: 6px; }
        
        .cell { background: #182232; border: 1px solid #2a374a; border-radius: 5px; padding: 6px; text-align: center; font-size: 0.75rem; font-weight: bold; color: #475569; min-height: 28px; display: flex; align-items: center; justify-content: center; }
    </style>
</head>
<body>

    <div class="top-bar">
        <div class="line-badge">B</div>
        <div class="stats-group">
            <div class="stat-box">
                <div class="stat-val" style="color:#22c55e;">{{SERV_COUNT}}</div>
                <div class="stat-lbl">En Servicio</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#38bdf8;">{{REQ_COUNT}}</div>
                <div class="stat-lbl">Requeridos</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#fbbf24;">{{DISP_COUNT}}</div>
                <div class="stat-lbl">Disponibles</div>
            </div>
        </div>
    </div>

    <div class="timer-bar">
        <div class="timer-clock">⏱️</div>
        <div>
            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Próximo Entre</div>
            <div class="timer-text">-</div>
        </div>
    </div>

    <!-- EN SERVICIO -->
    <div class="section-box">
        <div class="sec-title">En Servicio</div>
        <div class="grid-service">
            {{SERVICIO_GRID}}
        </div>
    </div>

    <!-- ANDÉN ROSAS -->
    <div class="section-box">
        <div class="sec-title">Andén Rosas</div>
        <div class="grid-2">
            <div class="cell"><span class="track-prefix">S</span></div>
            <div class="cell"><span class="track-prefix">N</span></div>
        </div>
    </div>

    <!-- COCHERA ROSAS -->
    <div class="section-box">
        <div class="sec-title">Cochera Rosas</div>
        <div class="grid-3">
            <div class="train-chip green"><span class="track-prefix">1</span>MITSUBISHI D</div>
            <div class="cell"><span class="track-prefix">1</span></div>
            <div class="cell"><span class="track-prefix">1</span></div>
            <div class="cell"><span class="track-prefix">3</span></div>
            <div class="cell"><span class="track-prefix">3</span></div>
            <div class="cell"><span class="track-prefix">3</span></div>
            <div class="train-chip green"><span class="track-prefix">4</span>CAF 6000 B1</div>
            <div class="cell"><span class="track-prefix">2</span></div>
            <div class="cell"><span class="track-prefix">2</span></div>
        </div>
    </div>

    <!-- TALLER URQUIZA -->
    <div class="section-box">
        <div class="sec-title">Taller Urquiza</div>
        <div class="grid-2">
            <div class="train-chip maroon"><span class="track-prefix">F1</span>CAF 6000 F1</div>
            <div class="train-chip maroon"><span class="track-prefix">F2</span>CAF 6000 H1</div>
        </div>
    </div>

    <!-- LOS INCAS -->
    <div class="section-box">
        <div class="sec-title">Los Incas</div>
        <div class="grid-2">
            <div class="cell"><span class="track-prefix">S</span></div>
            <div class="cell"><span class="track-prefix">N</span></div>
        </div>
    </div>

    <!-- RUBÉN DARÍO -->
    <div class="section-box">
        <div class="sec-title">Rubén Darío</div>
        <div class="grid-1"><div class="cell"></div></div>
    </div>

    <!-- ALEM -->
    <div class="section-box">
        <div class="sec-title">Alem</div>
        <div class="grid-2">
            <div class="cell"><span class="track-prefix">S</span></div>
            <div class="cell"><span class="track-prefix">N</span></div>
        </div>
    </div>

    <!-- ECHEVERRÍA -->
    <div class="section-box">
        <div class="sec-title">Echeverría</div>
        <div class="grid-2">
            <div class="cell"><span class="track-prefix">N</span></div>
            <div class="cell"><span class="track-prefix">N</span></div>
            <div class="cell"><span class="track-prefix">S</span></div>
            <div class="cell"><span class="track-prefix">S</span></div>
        </div>
    </div>

    <!-- TALLER RANCAGUA -->
    <div class="section-box">
        <div class="sec-title">Taller Rancagua</div>
        <div style="display:flex; flex-direction:column; gap:6px;">
            <div class="grid-2"><div class="cell"><span class="track-prefix">2</span></div><div class="cell"></div></div>
            <div class="grid-1"><div class="cell"><span class="track-prefix">3</span></div></div>
            <div class="grid-1"><div class="train-chip red"><span class="track-prefix">4</span>MITSUBISHI A</div></div>
            <div class="grid-1"><div class="train-chip black"><span class="track-prefix">5</span>MITSUBISHI C</div></div>
            <div class="grid-3"><div class="cell"><span class="track-prefix">6</span></div><div class="cell"></div><div class="train-chip striped"><span class="track-prefix">6</span>500-916-017</div></div>
            <div class="grid-2"><div class="cell"><span class="track-prefix">7</span></div><div class="cell"></div></div>
            <div class="grid-1"><div class="cell"><span class="track-prefix">8</span></div></div>
            <div class="grid-1"><div class="cell"><span class="track-prefix">9</span></div></div>
            <div class="grid-2"><div class="cell"><span class="track-prefix">10</span></div><div class="cell"></div></div>
            <div class="grid-1"><div class="cell"><span class="track-prefix">D</span></div></div>
        </div>
    </div>

    <!-- LYNCH -->
    <div class="section-box">
        <div class="sec-title">Lynch</div>
        <div class="grid-3">
            <div class="train-chip maroon">CAF 6000 D1</div>
            <div class="cell"></div>
            <div class="cell"></div>
        </div>
    </div>

    <!-- POLVORÍN -->
    <div class="section-box">
        <div class="sec-title">Polvorín</div>
        <div class="grid-3">
            <div class="train-chip striped">OCUPADA</div>
            <div class="cell"></div>
            <div class="cell"></div>
        </div>
    </div>

    <!-- TJC -->
    <div class="section-box">
        <div class="sec-title">TJC</div>
        <div class="grid-3">
            <div class="cell"></div>
            <div class="train-chip maroon">CAF 6000 C1</div>
            <div class="train-chip maroon">CAF 6000 L1</div>
        </div>
    </div>

</body>
</html>"""

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/tablero')
def tablero_view():
    raw_token = os.environ.get("AUTH_TOKEN", "")
    auth_token = raw_token.strip().strip("'").strip('"').replace('\n', '').replace('\r', '')

    headers = {
        "x-auth-token": auth_token,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "Origin": EMOVA_BASE,
        "Referer": f"{EMOVA_BASE}/ce/#/lineaB"
    }

    itinerarios = [
        {"n": 3, "f": "MITSUBISHI H", "c": "green"},
        {"n": 11, "f": "MITSUBISHI K", "c": "green"},
        {"n": 13, "f": "MITSUBISHI L", "c": "green"},
        {"n": 1, "f": "CAF 6000 H1", "c": "green"},
        {"n": 4, "f": "MITSUBISHI E", "c": "green"},
        {"n": 21, "f": "-", "c": "empty"},
        {"n": 5, "f": "MITSUBISHI N", "c": "green"},
        {"n": 17, "f": "MITSUBISHI Q", "c": "green"},
        {"n": 14, "f": "CAF 6000 N1", "c": "green"},
        {"n": 12, "f": "CAF 6000 K1", "c": "green"},
        {"n": 22, "f": "-", "c": "empty"},
        {"n": 2, "f": "MITSUBISHI I", "c": "green"},
        {"n": 6, "f": "MITSUBISHI O", "c": "green"},
        {"n": 18, "f": "MITSUBISHI P", "c": "green"},
        {"n": 19, "f": "MITSUBISHI G", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 7, "f": "CAF 6000 E1", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 15, "f": "-", "c": "empty"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 8, "f": "MITSUBISHI T", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 9, "f": "CAF 6000 M1", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 20, "f": "CAF 6000 J1", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 16, "f": "CAF 6000 G1", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"},
        {"n": 10, "f": "MITSUBISHI M", "c": "green"},
        {"n": 40, "f": "-", "c": "empty"}
    ]

    serv_count = "19"
    req_count = "18"
    disp_count = "21"

    try:
        r = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=4)
        if r.status_code == 200:
            data = r.json() or {}
            serv_count = str(data.get("enServicio", serv_count))
            req_count = str(data.get("requeridos", req_count))
            disp_count = str(data.get("disponibles", disp_count))
    except Exception:
        pass

    servicio_html = ""
    for item in itinerarios:
        if item["c"] == "empty":
            servicio_html += '<div class="service-row"><div class="itin-num">' + str(item["n"]) + '</div><div class="train-chip empty">-</div></div>'
        else:
            servicio_html += '<div class="service-row"><div class="itin-num">' + str(item["n"]) + '</div><div class="train-chip ' + item["c"] + '">' + item["f"] + '</div></div>'

    html = HTML_BASE.replace("{{SERV_COUNT}}", serv_count)\
                    .replace("{{REQ_COUNT}}", req_count)\
                    .replace("{{DISP_COUNT}}", disp_count)\
                    .replace("{{SERVICIO_GRID}}", servicio_html)

    return Response(html, content_type='text/html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
