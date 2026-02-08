from flask import Flask, request, jsonify
import requests
import json
import os

# Vercel apne aap is 'app' ko dhoond lega
app = Flask(__name__)

# Ye line har request ko pakad legi (chahe /api ho ya /api/index)
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # 1. API Key Check
    api_key = os.environ.get("GEMINI_API_KEY")
    
    # Agar key nahi mili
    if not api_key:
        return jsonify({
            "answer": "Error: Vercel Settings me API Key nahi mili! (Settings > Env Variables check karein)"
        })

    # 2. Browser Check (GET request)
    if request.method == 'GET':
        return jsonify({
            "status": "Alive",
            "message": "Badhai ho! Server chal gaya. Ab Chat try karo."
        })

    # 3. Chat Logic (POST request)
    try:
        data = request.json
        user_msg = data.get('question', '')

        if not user_msg:
            return jsonify({"answer": "Empty message mat bhejo bhai."})

        # Google API Call
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        payload = {"contents": [{"parts": [{"text": user_msg}]}]}
        headers = {'Content-Type': 'application/json'}

        # Request bhejo
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            return jsonify({"answer": response.json()['candidates'][0]['content']['parts'][0]['text']})
        else:
            return jsonify({"answer": f"Google Error ({response.status_code}): {response.text}"})

    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}"})

# NOTE: Niche 'def handler' wali line MAT likhna. Vercel smart hai.
