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
        return jsonify({"answer": "Error: API Key missing in Vercel Settings!"})

    # 2. Browser Check (GET request)
    if request.method == 'GET':
        return jsonify({"status": "Online", "message": "Server is Running on Gemini Pro (Stable)!"})

    # 3. Chat Logic
    try:
        data = request.json
        user_msg = data.get('question', '')

        if not user_msg:
            return jsonify({"answer": "Empty message."})

        # --- FIX: Sabse Stable Model Use Karo ---
        # 'gemini-1.5-flash' mein naam ka lafda ho raha hai (404).
        # 'gemini-pro' sabse purana aur stable hai. Ye kabhi 404 nahi deta.
        model_name = "gemini-pro"
        
        # URL construction
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        
        payload = {"contents": [{"parts": [{"text": user_msg}]}]}
        headers = {'Content-Type': 'application/json'}

        # Request bhejo
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return jsonify({"answer": response.json()['candidates'][0]['content']['parts'][0]['text']})
        else:
            # Agar ab bhi error aaye, toh error code wapas karo
            return jsonify({"answer": f"Google Error: {response.status_code} - {response.text}"})

    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})
        
