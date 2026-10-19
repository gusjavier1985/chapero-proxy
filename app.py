import os
import requests
from flask import Flask, jsonify, Response, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

EMOVA_BASE = "https://chapero.emova.com.ar"

@app.route('/')
def home():
    return jsonify({"status": "ok", "message": "API Proxy Activa 🚆"})

@app.route('/tablero')
def tablero_view():
    raw_token = os.environ.get("AUTH_TOKEN", "")
    auth_token = raw_token.strip().strip("'").strip('"').replace('\n', '').replace('\r', '')

    # Plantilla HTML que embebe la vista oficial de Emova e inyecta la autenticación automáticamente
    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chapero Línea B</title>
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                overflow: hidden;
                background-color: #0d1117;
            }}
            iframe {{
                width: 100%;
                height: 100%;
                border: none;
            }}
        </style>
    </head>
    <body>
        <script>
            // Guardar token en el almacenamiento local antes de cargar el Chapero oficial
            localStorage.setItem("token", "{auth_token}");
            localStorage.setItem("x-auth-token", "{auth_token}");
            
            // Redirección al tablero de la Línea B
            window.location.href = "{EMOVA_BASE}/ce/#/lineaB";
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/api/posiciones-linea-b', methods=['GET'])
def posiciones_linea_b():
    raw_token = os.environ.get("AUTH_TOKEN", "")
    auth_token = raw_token.strip().strip("'").strip('"').replace('\n', '').replace('\r', '')

    headers = {
        "x-auth-token": auth_token,
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Origin": EMOVA_BASE,
        "Referer": f"{EMOVA_BASE}/ce/#/lineaB"
    }

    try:
        r = requests.get(f"{EMOVA_BASE}/api/ce/requerimientosDia", headers=headers, timeout=5)
        return Response(r.content, status=r.status_code, content_type=r.headers.get('Content-Type'))
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
