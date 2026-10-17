import os
import requests
from flask import Flask, Response, request

app = Flask(__name__)

EMOVA_USER = os.environ.get("EMOVA_USER", "")
EMOVA_PASS = os.environ.get("EMOVA_PASS", "")
EMOVA_BASE = "https://chapero.emova.com.ar"

# Sesión global para mantener las cookies y credenciales activas
session = requests.Session()
is_logged_in = False

def ensure_logged_in():
    global is_logged_in
    if not is_logged_in:
        try:
            login_url = f"{EMOVA_BASE}/api/login"
            session.post(login_url, json={"usuario": EMOVA_USER, "password": EMOVA_PASS}, timeout=10)
            is_logged_in = True
        except Exception as e:
            print(f"Error en login automático: {e}")

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    ensure_logged_in()
    target_url = f"{EMOVA_BASE}/{path}"
    if request.query_string:
        target_url += f"?{request.query_string.decode('utf-8')}"
        
    # Copiamos los headers del navegador del usuario
    headers = {key: value for (key, value) in request.headers if key.lower() != 'host'}
    
    try:
        if request.method == 'POST':
            resp = session.post(target_url, data=request.form, json=request.json, headers=headers, allow_redirects=False, timeout=15)
        else:
            resp = session.get(target_url, headers=headers, allow_redirects=False, timeout=15)
            
        # Filtramos headers de conexión para evitar conflictos
        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        resp_headers = [(name, value) for (name, value) in resp.raw.headers.items() if name.lower() not in excluded_headers]
        
        return Response(resp.content, resp.status_code, resp_headers)
    except Exception as e:
        return f"Error en el proxy: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
