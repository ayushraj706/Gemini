import os
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# Vercel Environment Variable se Key lega
MY_API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route('/api', methods=['POST'])
def handle_request():
    # 1. Check Key
    if not MY_API_KEY:
        return jsonify({"answer": "Error: API Key missing in Vercel!"})

    try:
        data = request.json
        user_msg = data.get('question', '')

        # 2. Google Gemini API Call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={MY_API_KEY}"
        payload = {"contents": [{"parts": [{"text": user_msg}]}]}
        
        headers = {'Content-Type': 'application/json'}
        res = requests.post(url, headers=headers, data=json.dumps(payload))
        
        # 3. Jawab bhejo
        if res.status_code == 200:
            answer = res.json()['candidates'][0]['content']['parts'][0]['text']
            return jsonify({"answer": answer.strip()})
        else:
            return jsonify({"answer": f"Error: Google ne mana kar diya ({res.status_code})"})

    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})

# Vercel handler
def handler(request):
    return app(request)
  
