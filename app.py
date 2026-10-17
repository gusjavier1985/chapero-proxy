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
        # Descargamos la estructura base de la página de Emova
        resp = requests.get(EMOVA_BASE, timeout=10)
        html_content = resp.text
        
        # Script automático que se ejecuta en el navegador del usuario para loguearse solo
        auto_login_script = f"""
        <script>
            window.addEventListener('DOMContentLoaded', () => {{
                setTimeout(() => {{
                    const inputs = document.querySelectorAll('input');
                    let userInp = null, passInp = null;
                    inputs.forEach(i => {{
                        if (i.type === 'text' || i.type === 'email' || i.placeholder?.toLowerCase().includes('usuario')) userInp = i;
                        if (i.type === 'password') passInp = i;
                    }});
                    
                    if (userInp && passInp) {{
                        userInp.value = "{EMOVA_USER}";
                        userInp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        passInp.value = "{EMOVA_PASS}";
                        passInp.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        
                        const buttons = document.querySelectorAll('button, input[type="submit"]');
                        buttons.forEach(b => {{
                            if (b.innerText.toLowerCase().includes('ingresar') || b.value.toLowerCase().includes('ingresar')) {{
                                b.click();
                            }}
                        }});
                    }}
                }}, 500);
            });
        </script>
        """
        
        # Inyectamos el base href para los estilos y el script de auto-login
        if "<head>" in html_content:
            html_content = html_content.replace("<head>", f'<head><base href="{EMOVA_BASE}/">')
            
        if "</body>" in html_content:
            html_content = html_content.replace("</body>", f"{auto_login_script}</body>")
        else:
            html_content += auto_login_script
            
        return Response(html_content, content_type="text/html")
        
    except Exception as e:
        return f"<h3>Error al conectar:</h3><p>{str(e)}</p>", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
