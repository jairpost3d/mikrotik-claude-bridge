import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Obtener claves de las variables de entorno
CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')
MIKROTIK_IP = os.environ.get('MIKROTIK_IP', "192.168.88.1")
MIKROTIK_USER = os.environ.get('MIKROTIK_USER', "admin")
MIKROTIK_PASS = os.environ.get('MIKROTIK_PASS')

@app.route('/ask-claude', methods=['POST'])
def ask_claude():
    data = request.json
    prompt = data.get('prompt', '')
    context = data.get('context', '')

    full_prompt = f"""
    Eres un experto en redes Mikrotik RouterOS.
    Tu tarea es devolver SOLO un JSON válido con una de estas acciones:
    1. {{ "action": "execute", "command": "/ip route print" }}
    2. {{ "action": "reply", "message": "La interfaz ether1 está caída." }}
    3. {{ "action": "fetch", "command": "/interface print" }}
    
    Contexto: {context}
    Solicitud: {prompt}
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
            return jsonify({"action": "reply", "message": claude_text})
        else:
            return jsonify({"action": "reply", "message": "Error: Sin respuesta de Claude"})
            
    except Exception as e:
        return jsonify({"action": "reply", "message": f"Error: {str(e)}"})

# Handler para Vercel
def handler(request):
    return ask_claude(request)
