import os
from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# --- AB HUM KEY YAHAN NAHI LIKHENGE (Security ke liye) ---
# Vercel mein 'GEMINI_API_KEY' naam ka variable banayein
MY_API_KEY = os.environ.get("GEMINI_API_KEY")

def get_active_model():
    if not MY_API_KEY:
        return "error_no_key"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={MY_API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'models' in data:
            # Flash 1.5 sabse best hai
            for m in data['models']:
                if "gemini-1.5-flash" in m['name']: return m['name']
            return data['models'][0]['name']
    except: pass
    return "models/gemini-1.5-flash"

@app.route('/ask', methods=['POST'])
def ask_gemini():
    if not MY_API_KEY:
        return jsonify({"answer": "Error: Vercel mein API Key set nahi hai!"})

    try:
        data = request.json
        user_msg = data.get('question')
        sender = data.get('sender_name', 'Dost')
        training = data.get('training_data', 'Tu Ayush ka assistant hai.')

        model = get_active_model()
        prompt = f"{training.replace('%name%', sender)}\n\nUser: {user_msg}\nReply:"

        url = f"https://generativelanguage.googleapis.com/v1beta/{model}:generateContent?key={MY_API_KEY}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        
        res = requests.post(url, json=payload)
        if res.status_code == 200:
            return jsonify({"answer": res.json()['candidates'][0]['content']['parts'][0]['text']})
        else:
            return jsonify({"answer": f"Google Error: {res.status_code}. Key rotate karni hogi."})

    except Exception as e:
        return jsonify({"answer": f"System Error: {str(e)}"})
     
