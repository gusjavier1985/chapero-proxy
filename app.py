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
    <title>Chapero Electrónico - Línea B</title>
    <style>
        * { box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
        body { background-color: #0d131f; color: #ffffff; margin: 0; padding: 8px; font-size: 12px; }
        
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
        .itin-num { width: 24px; font-weight: bold; font-size: 0.75rem; color: #94a3b8; text-align: center; }
        
        .train-chip { flex: 1; font-weight: bold; font-size: 0.75rem; padding: 5px; border-radius: 4px; text-align: center; border: 1px solid transparent; }
        .train-chip.empty { background: #182232; border: 1px dashed #2a374a; color: #475569; }
        .train-chip.green { background: #15803d; border-color: #22c55e; color: #fff; }
        .train-chip.red { background: #b91c1c; border-color: #ef4444; color: #fff; }
        .train-chip.maroon { background: #581c87; border-color: #7e22ce; color: #e9d5ff; }
        .train-chip.striped { background: repeating-linear-gradient(45deg, #854d0e, #854d0e 10px, #713f12 10px, #713f12 20px); border-color: #a16207; color: #fff; font-size: 0.7rem; }

        .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
        .grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
        .grid-1 { display: grid; grid-template-columns: 1fr; gap: 6px; }
        
        .cell { background: #182232; border: 1px solid #2a374a; border-radius: 5px; padding: 6px; text-align: center; font-size: 0.75rem; font-weight: bold; color: #475569; min-height: 28px; }
        .track-num { font-size: 0.65rem; color: #64748b; margin-right: 4px; }
    </style>
</head>
<body>

    <div class="top-bar">
        <div class="line-badge">B</div>
        <div class="stats-group">
            <div class="stat-box">
                <div class="stat-val" style="color:#22c55e;">20</div>
                <div class="stat-lbl">En Servicio</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#38bdf8;">20</div>
                <div class="stat-lbl">Requeridos</div>
            </div>
            <div class="stat-box">
                <div class="stat-val" style="color:#fbbf24;">21</div>
                <div class="stat-lbl">Disponibles</div>
            </div>
        </div>
    </div>

    <div class="timer-bar">
        <div class="timer-clock">⏱️</div>
        <div>
            <div style="font-size: 0.6rem; color: #94a3b8; text-transform: uppercase;">Próximo Entre</div>
            <div class="timer-text">56m</div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">En Servicio</div>
        <div class="grid-service">
            <div class="service-row"><div class="itin-num">3</div><div class="train-chip green">MITSUBISHI H</div></div>
            <div class="service-row"><div class="itin-num">11</div><div class="train-chip green">MITSUBISHI K</div></div>
            <div class="service-row"><div class="itin-num">13</div><div class="train-chip green">MITSUBISHI L</div></div>
            <div class="service-row"><div class="itin-num">1</div><div class="train-chip green">CAF 6000 H1</div></div>
            <div class="service-row"><div class="itin-num">4</div><div class="train-chip green">MITSUBISHI O</div></div>
            <div class="service-row"><div class="itin-num">21</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">5</div><div class="train-chip green">MITSUBISHI N</div></div>
            <div class="service-row"><div class="itin-num">17</div><div class="train-chip green">MITSUBISHI Q</div></div>
            <div class="service-row"><div class="itin-num">14</div><div class="train-chip green">CAF 6000 N1</div></div>
            <div class="service-row"><div class="itin-num">12</div><div class="train-chip green">CAF 6000 K1</div></div>
            <div class="service-row"><div class="itin-num">22</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">2</div><div class="train-chip green">MITSUBISHI I</div></div>
            <div class="service-row"><div class="itin-num">6</div><div class="train-chip green">MITSUBISHI O</div></div>
            <div class="service-row"><div class="itin-num">18</div><div class="train-chip green">MITSUBISHI P</div></div>
            <div class="service-row"><div class="itin-num">19</div><div class="train-chip green">MITSUBISHI G</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">7</div><div class="train-chip green">CAF 6000 E1</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">15</div><div class="train-chip green">MITSUBISHI D</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">8</div><div class="train-chip green">MITSUBISHI T</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">9</div><div class="train-chip green">CAF 6000 M1</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">20</div><div class="train-chip green">CAF 6000 J1</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">16</div><div class="train-chip green">CAF 6000 G1</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
            <div class="service-row"><div class="itin-num">10</div><div class="train-chip green">MITSUBISHI M</div></div>
            <div class="service-row"><div class="itin-num">40</div><div class="train-chip empty">-</div></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Andén Rosas</div>
        <div class="grid-2">
            <div class="cell"><span class="track-num">S</span></div>
            <div class="cell"><span class="track-num">N</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Cochera Rosas</div>
        <div class="grid-3">
            <div class="cell"><span class="track-num">1</span></div>
            <div class="cell"><span class="track-num">1</span></div>
            <div class="cell"><span class="track-num">1</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="cell train-chip green" style="padding:6px;"><span class="track-num">4</span>CAF 6000 B1</div>
            <div class="cell"><span class="track-num">2</span></div>
            <div class="cell"><span class="track-num">2</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Taller Urquiza</div>
        <div class="grid-2">
            <div class="train-chip maroon"><span class="track-num">F1</span>CAF 6000 F1</div>
            <div class="train-chip maroon"><span class="track-num">F2</span>CAF 6000 H1</div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Los Incas</div>
        <div class="grid-2">
            <div class="cell"><span class="track-num">S</span></div>
            <div class="cell"><span class="track-num">N</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Rubén Darío</div>
        <div class="grid-1"><div class="cell"></div></div>
    </div>

    <div class="section-box">
        <div class="sec-title">Alem</div>
        <div class="grid-2">
            <div class="cell"><span class="track-num">S</span></div>
            <div class="cell"><span class="track-num">N</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Echeverría</div>
        <div class="grid-2">
            <div class="cell"><span class="track-num">N</span></div>
            <div class="cell"><span class="track-num">S</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Taller Rancagua</div>
        <div class="grid-2">
            <div class="cell"><span class="track-num">2</span></div>
            <div class="cell"><span class="track-num">3</span></div>
            <div class="train-chip red"><span class="track-num">4</span>MITSUBISHI A</div>
            <div class="train-chip red"><span class="track-num">5</span>MITSUBISHI C</div>
            <div class="train-chip striped"><span class="track-num">6</span>500-916-017</div>
            <div class="cell"><span class="track-num">7</span></div>
            <div class="cell"><span class="track-num">8</span></div>
            <div class="cell"><span class="track-num">9</span></div>
            <div class="cell"><span class="track-num">10</span></div>
            <div class="cell"><span class="track-num">D</span></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Lynch</div>
        <div class="grid-3">
            <div class="train-chip maroon">CAF 6000 D1</div>
            <div class="cell"></div>
            <div class="cell"></div>
        </div>
    </div>

    <div class="section-box">
        <div class="sec-title">Polvorín</div>
        <div class="grid-3">
            <div class="train-chip striped">OCUPADA</div>
            <div class="cell"></div>
            <div class="cell"></div>
        </div>
    </div>

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
    return Response(HTML_TEMPLATE, content_type='text/html')

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
