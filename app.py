import os
import requests
from flask import Flask, Response

app = Flask(__name__)

# Las credenciales se leen desde Render, no quedan expuestas en GitHub
EMOVA_USER = os.environ.get("EMOVA_USER")
EMOVA_PASS = os.environ.get("EMOVA_PASS")

@app.route('/')
def home():
    return "Proxy Chapero Activo 🚆"

@app.route('/ver-chapero')
def ver_chapero():
    try:
        session = requests.Session()
        
        # Intento de autenticación
        login_url = "https://chapero.emova.com.ar/api/login"
        payload = {"usuario": EMOVA_USER, "password": EMOVA_PASS}
        session.post(login_url, json=payload, timeout=10)
        
        # Solicitud a la vista de la Línea B
        target_url = "https://chapero.emova.com.ar/ce/#/lineaB"
        response = session.get(target_url, timeout=10)
        
        return Response(response.content, content_type=response.headers.get('Content-Type', 'text/html'))
    except Exception as e:
        return f"Error al conectar: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
