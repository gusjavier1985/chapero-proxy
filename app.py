import os
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
    # Página puente con auto-envío de credenciales por formulario oficial
    bridge_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Autenticando Línea B...</title>
        <style>
            body {{ background-color: #121212; color: #ffffff; font-family: sans-serif; text-align: center; padding-top: 25vh; }}
            .spinner {{ border: 4px solid rgba(255,255,255,0.1); width: 40px; height: 40px; border-radius: 50%; border-left-color: #09f; animation: spin 1s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        </style>
    </head>
    <body>
        <h3>Conectando con el Chapero Electrónico...</h3>
        <div class="spinner"></div>
        <p>Iniciando sesión de forma segura...</p>

        <!-- Formulario oculto que realiza el login nativo en el navegador -->
        <form id="loginForm" action="{EMOVA_BASE}/api/login" method="POST" style="display:none;">
            <input type="hidden" name="usuario" value="{EMOVA_USER}">
            <input type="hidden" name="password" value="{EMOVA_PASS}">
        </form>

        <script>
            setTimeout(() => {{
                // Enviamos el formulario automáticamente y luego saltamos a la Línea B
                const form = document.getElementById('loginForm');
                if (form) {{
                    fetch(form.action, {{
                        method: 'POST',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ usuario: "{EMOVA_USER}", password: "{EMOVA_PASS}" }})
                    }}).then(() => {{
                        window.location.href = "{EMOVA_BASE}/ce/#/lineaB";
                    }}).catch(() => {{
                        window.location.href = "{EMOVA_BASE}/ce/#/lineaB";
                    }});
                }} else {{
                    window.location.href = "{EMOVA_BASE}/ce/#/lineaB";
                }}
            }}, 400);
        </script>
    </body>
    </html>
    """
    return Response(bridge_html, content_type="text/html")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
