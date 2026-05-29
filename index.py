import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

CLAUDE_API_KEY = os.environ.get('CLAUDE_API_KEY')

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

# Función handler OBLIGATORIA para Vercel
def handler(request):
    # Vercel pasa la solicitud como un objeto, necesitamos extraer los datos
    if request.method == 'POST':
        # Obtener el cuerpo de la solicitud
        body = request.body
        import json
        data = json.loads(body)
        
        prompt = data.get('prompt', '')
        context = data.get('context', '')
        
        # Llamar a ask_claude con los datos extraídos
        return ask_claude(prompt, context)
    else:
        return jsonify({"error": "Método no permitido"}), 405
