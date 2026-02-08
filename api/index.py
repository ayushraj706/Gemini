from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# --- FIX: Route ko '/' kar diya taaki 404 na aaye ---
@app.route('/', methods=['GET', 'POST'])
def home():
    # 1. API Key Check
    MY_API_KEY = os.environ.get("GEMINI_API_KEY")
    if not MY_API_KEY:
        return jsonify({"answer": "Error: Vercel Settings mein API Key nahi mili!"})

    # 2. Agar GET request hai (Browser check)
    if request.method == 'GET':
        return jsonify({"status": "Active", "message": "Engine chal raha hai bhai!"})

    # 3. Agar POST request hai (Chat message)
    try:
        data = request.json
        user_msg = data.get('question', '')

        if not user_msg:
            return jsonify({"answer": "Khali message mat bhejo!"})

        # Google Gemini Call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={MY_API_KEY}"
        payload = {"contents": [{"parts": [{"text": user_msg}]}]}
        headers = {'Content-Type': 'application/json'}

        res = requests.post(url, headers=headers, data=json.dumps(payload))

        if res.status_code == 200:
            answer = res.json()['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"answer": answer.strip()})
        else:
            return jsonify({"answer": f"Google Error: {res.status_code} - {res.text}"})

    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})

# Vercel handler
def handler(request):
    return app(request)
    
