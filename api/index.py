from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Ye code kisi bhi raste (Route) se aayi request ko pakad lega
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # 1. API Key Check
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"answer": "Error: API Key missing in Vercel Settings!"})

    # 2. Agar koi browser se check kare
    if request.method == 'GET':
        return jsonify({"status": "Online", "message": "Bhai Server Mast Chal Raha Hai!"})

    # 3. Chat Message Handling
    try:
        data = request.json
        user_msg = data.get('question', '')
        
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": user_msg}]}]}
        headers = {'Content-Type': 'application/json'}
        
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        
        if response.status_code == 200:
            return jsonify({"answer": response.json()['candidates'][0]['content']['parts'][0]['text']})
        else:
            return jsonify({"answer": f"Google Error: {response.text}"})

    except Exception as e:
        # Ye batayega ki server kyu crash hua
        return jsonify({"answer": f"Server Crash Error: {str(e)}"})

# Vercel start point
def handler(request):
    return app(request)
    
