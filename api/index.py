from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

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

        # --- FIX: Stable Model Use Karo (High Limit) ---
        # 2.5-flash ka limit sirf 20 tha, 1.5-flash ka limit 1500 hai.
        model_name = "models/gemini-1.5-flash"
        
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
        
