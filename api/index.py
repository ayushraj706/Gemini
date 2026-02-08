from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['POST'])
def handle_request(path):
    data = request.json
    user_msg = data.get('question', '')
    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        return jsonify({"answer": "Error: API Key missing in Vercel Settings!"})

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": user_msg}]}]}
    headers = {'Content-Type': 'application/json'}

    try:
        res = requests.post(url, headers=headers, json=payload)
        if res.status_code == 200:
            return jsonify({"answer": res.json()['candidates'][0]['content']['parts'][0]['text']})
        else:
            return jsonify({"answer": f"Google Error: {res.status_code}"})
    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})
        
