import os
import requests
from flask import Flask, Response, request, redirect

app = Flask(__name__)

EMOVA_USER = os.environ.get("EMOVA_USER", "")
EMOVA_PASS = os.environ.get("EMOVA_PASS", "")
EMOVA_BASE = "https://chapero.emova.com.ar"

@app.route('/')
def home():
    return "Proxy Chapero Activo 🚆"

@app.route('/ver-chapero')
def ver_chapero():
    try:
        session = requests.Session()
        
        # 1. Intentar Login en Emova
        login_url = f"{EMOVA_BASE}/api/login"
        payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        login_res = session.post(login_url, json=payload, headers=headers, timeout=10)
        
        # 2. Pedir la vista de la Línea B
        target_url = f"{EMOVA_BASE}/ce/#/lineaB"
        resp = session.get(target_url, headers=headers, timeout=10)
        
        # Inyectar etiqueta base para que cargue los estilos y scripts desde Emova
        content = resp.text
        if "<head>" in content:
            content = content.replace("<head>", f'<head><base href="{EMOVA_BASE}/ce/">')
            
        return Response(content, content_type="text/html")
        
    except Exception as e:
        return f"<h3>Error al conectar con Emova:</h3><p>{str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
