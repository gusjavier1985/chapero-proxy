import os
import requests
from flask import Flask, jsonify, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chapero Electrónico - Línea B (En Vivo)</title>
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
                <div class="stat-val" id="cnt-serv" style="color:#22c55e;">--</div>
                <div class="stat-lbl">En Servicio</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" id="cnt-req" style="color:#38bdf8;">--</div>
                <div class="stat-lbl">Requeridos</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" id="cnt-disp" style="color:#fbbf24;">--</div>
                <div class="stat-lbl">Disponibles</div>
            </div>
        </div>
    </div>

    <div class="timer-bar">
        <div class="timer-clock">⏱️</div>
        <div>
            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Próximo Entre</div>
            <div class="timer-text" id="timer-val">-</div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">En Servicio</div>
        <div id="service-grid" class="grid-service">
            <div class="cell" style="grid-column: span 2;">Cargando posiciones en vivo...</div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Andén Rosas</div>
        <div class="grid-2">
            <div class="cell" id="rosas-s"><span class="track-prefix">S</span></div>
            <div class="cell" id="rosas-n"><span class="track-prefix">N</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Cochera Rosas</div>
        <div class="grid-3" id="cochera-rosas-grid">
            <div class="cell" id="cr-1a"><span class="track-prefix">1</span></div>
            <div class="cell" id="cr-1b"><span class="track-prefix">1</span></div>
            <div class="cell" id="cr-1c"><span class="track-prefix">1</span></div>
            <div class="cell" id="cr-3a"><span class="track-prefix">3</span></div>
            <div class="cell" id="cr-3b"><span class="track-prefix">3</span></div>
            <div class="cell" id="cr-3c"><span class="track-prefix">3</span></div>
            <div class="cell" id="cr-4a"><span class="track-prefix">4</span></div>
            <div class="cell" id="cr-2a"><span class="track-prefix">2</span></div>
            <div class="cell" id="cr-2b"><span class="track-prefix">2</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Taller Urquiza</div>
        <div class="grid-2">
            <div class="cell" id="urq-f1"><span class="track-prefix">F1</span></div>
            <div class="cell" id="urq-f2"><span class="track-prefix">F2</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Taller Rancagua</div>
        <div style="display:flex; flex-direction:column; gap:6px;">
            <div class="grid-2"><div class="cell" id="ran-2a"><span class="track-prefix">2</span></div><div class="cell" id="ran-2b"></div></div>
            <div class="grid-1"><div class="cell" id="ran-3"><span class="track-prefix">3</span></div></div>
            <div class="grid-1"><div class="cell" id="ran-4"><span class="track-prefix">4</span></div></div>
            <div class="grid-1"><div class="cell" id="ran-5"><span class="track-prefix">5</span></div></div>
            <div class="grid-3"><div class="cell" id="ran-6a"><span class="track-prefix">6</span></div><div class="cell" id="ran-6b"></div><div class="cell" id="ran-6c"><span class="track-prefix">6</span></div></div>
            <div class="grid-2"><div class="cell" id="ran-7a"><span class="track-prefix">7</span></div><div class="cell" id="ran-7b"></div></div>
            <div class="grid-1"><div class="cell" id="ran-8"><span class="track-prefix">8</span></div></div>
            <div class="grid-1"><div class="cell" id="ran-9"><span class="track-prefix">9</span></div></div>
            <div class="grid-2"><div class="cell" id="ran-10a"><span class="track-prefix">10</span></div><div class="cell" id="ran-10b"></div></div>
            <div class="grid-1"><div class="cell" id="ran-d"><span class="track-prefix">D</span></div></div>
        </div>
    </div>

    <script>
        async function sincronizarEnVivo() {
            try {
                const res = await fetch('/api/posiciones-linea-b');
                if(!res.ok) return;
                const json = await res.json();

                if (json.status === "success") {
                    if (json.resumen) {
                        document.getElementById('cnt-serv').innerText = json.resumen.enServicio || "--";
                        document.getElementById('cnt-req').innerText = json.resumen.requeridos || "--";
                        document.getElementById('cnt-disp').innerText = json.resumen.disponibles || "--";
                    }

                    if (json.servicio && json.servicio.length > 0) {
                        let html = '';
                        json.servicio.forEach(item => {
                            if (item.f) {
                                html += '<div class="service-row"><div class="itin-num">' + item.n + '</div><div class="train-chip green">' + item.f + '</div></div>';
                            } else {
                                html += '<div class="service-row"><div class="itin-num">' + item.n + '</div><div class="train-chip empty">-</div></div>';
                            }
                        });
                        document.getElementById('service-grid').innerHTML = html;
                    }
                }
            } catch (e) {
                console.error("Error sincronizando en vivo:", e);
            }
        }

        sincronizarEnVivo();
        setInterval(sincronizarEnVivo, 5000);
    </script>
</body>
</html>"""

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/tablero')
def tablero_view():
    return Response(HTML_TEMPLATE, content_type='text/html')

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    raw_token = os.environ.get("AUTH_TOKEN", "")
    auth_token = raw_token.strip().strip("'").strip('"').replace('\n', '').replace('\r', '')

    headers = {
        "x-auth-token": auth_token,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
        "Origin": EMOVA_BASE,
        "Referer": f"{EMOVA_BASE}/ce/#/lineaB"
    }

    resumen = {"enServicio": "--", "requeridos": "--", "disponibles": "--"}
    servicio_lista = []

    try:
        r_req = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=4)
        if r_req.status_code == 200:
            data_req = r_req.json() or {}
            resumen = {
                "enServicio": data_req.get("enServicio", "--"),
                "requeridos": data_req.get("requeridos", "--"),
                "disponibles": data_req.get("disponibles", "--")
            }
    except Exception:
        pass

    return jsonify({
        "status": "success",
        "resumen": resumen,
        "servicio": servicio_lista
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
