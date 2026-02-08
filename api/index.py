from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# --- SMART FUNCTION: Google se poocho "Kon sa Model hai?" ---
def get_available_model(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(url)
        
        if res.status_code == 200:
            models = res.json().get('models', [])
            # List mein se wo model dhoondo jo 'generateContent' support karta ho
            for model in models:
                if "generateContent" in model.get("supportedGenerationMethods", []):
                    # Sabse pehla jo mile (Jaise 'models/gemini-1.5-flash' ya 'models/gemini-pro')
                    return model['name']
    except:
        pass
    # Agar list nahi mili, toh Safe fallback use karo
    return "models/gemini-1.5-flash"

# --- MAIN ROUTE ---
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # 1. API Key Check
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"answer": "Error: Vercel Settings me API Key nahi mili!"})

    # 2. Browser Check
    if request.method == 'GET':
        return jsonify({"status": "Online", "message": "Server Ready hai!"})

    # 3. Chat Logic
    try:
        data = request.json
        user_msg = data.get('question', '')

        if not user_msg:
            return jsonify({"answer": "Kuch likho toh sahi!"})

        # --- STEP 1: Google se poocho kon sa model use karein ---
        model_name = get_available_model(api_key)
        
        # --- STEP 2: Us model se jawab maango ---
        url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": user_msg}]}]}
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return jsonify({"answer": response.json()['candidates'][0]['content']['parts'][0]['text']})
        else:
            # Agar fail hua, toh error dikhao
            return jsonify({"answer": f"Google Error ({model_name}): {response.text}"})

    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})
        
