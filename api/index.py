from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Obtener claves de las variables de entorno (seguro)
CLAUDE_API_KEY = "FILL_WITH_ENV_VAR"
MIKROTIK_IP = os.environ.get('MIKROTIK_IP', "192.168.11.1")
MIKROTIK_USER = os.environ.get('MIKROTIK_USER', "claudeapi")
MIKROTIK_PASS = os.environ.get('MIKROTIK_PASS')

@app.route('/ask-claude', methods=['POST'])
def ask_claude():
    data = request.json
    prompt = data.get('prompt', '')
    context = data.get('context', '')

    # Prompt optimizado para Claude
    full_prompt = f"""
    Eres un experto en redes Mikrotik RouterOS.
    Tu tarea es analizar la solicitud y devolver SOLO un JSON válido con una de estas acciones:
    1. {{ "action": "execute", "command": "/ip route print" }} (para ejecutar un comando)
    2. {{ "action": "reply", "message": "La interfaz ether1 está caída." }} (para responder)
    3. {{ "action": "fetch", "command": "/interface print" }} (para obtener datos)
    
    Contexto: {context}
    Solicitud: {prompt}
    
    Reglas:
    - No uses markdown, solo JSON puro.
    - Si el comando requiere autenticación, asume que Mikrotik ya está configurado.
    - Si la solicitud es ambigua, devuelve un mensaje de respuesta pidiendo claridad.
    """

    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "Content-Type": "application/json",
        "anthropic-version": "2023-06-01"
    }
    
    payload = {
        "model": "claude-3-sonnet-20240229",
        "max_tokens": 1000,
        "messages": [{"role": "user", "content": full_prompt}]
    }

    try:
        response = requests.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers, timeout=30)
        response_data = response.json()
        
        if "content" in response_data and response_data["content"]:
            claude_text = response_data["content"][0]["text"]
            # Intentar devolver el texto directamente si no es JSON
            return jsonify({"action": "reply", "message": claude_text})
        else:
            return jsonify({"action": "reply", "message": "Error: Sin respuesta de Claude"})
            
    except Exception as e:
        return jsonify({"action": "reply", "message": f"Error: {str(e)}"})

if __name__ == '__main__':
    app.run()