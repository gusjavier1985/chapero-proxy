import os
import requests
from flask import Flask, Response

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
        login_url = f"{EMOVA_BASE}/api/login"
        payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        # Realizamos el login invisible en el servidor
        res = session.post(login_url, json=payload, headers=headers, timeout=10)
        
        token_script = ""
        try:
            data = res.json()
            # Capturamos posibles tokens devueltos por la API de Emova
            token = data.get("token") or data.get("access_token") or data.get("accessToken")
            if token:
                token_script = f"localStorage.setItem('token', '{token}'); localStorage.setItem('access_token', '{token}');"
        except:
            pass

        # Página puente que inyecta la sesión y entra directo a la Línea B
        bridge_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <base href="{EMOVA_BASE}/ce/">
            <meta charset="UTF-8">
            <title>Abriendo Línea B...</title>
        </head>
        <body style="background-color: #121212; color: #ffffff; font-family: sans-serif; text-align: center; padding-top: 20vh;">
            <h3>Conectando con Línea B...</h3>
            <script>
                try {{
                    {token_script}
                }} catch (e) {{}}
                
                // Redirección automática al panel de la Línea B
                setTimeout(() => {{
                    window.location.href = "{EMOVA_BASE}/ce/#/lineaB";
                }}, 300);
            </script>
        </body>
        </html>
        """
        return Response(bridge_html, content_type="text/html")
        
    except Exception as e:
        return f"<h3>Error al conectar con Emova:</h3><p>{str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
