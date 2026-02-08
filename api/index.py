from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json
import os
import re
import random

app = Flask(__name__)

# --- MEMORY FOR OTP (Temporary) ---
otp_storage = {}

# --- HELPER FUNCTIONS ---
def extract_video_id(url):
    patterns = [r'(?:v=|\/)([0-9A-Za-z_-]{11}).*', r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})']
    for pattern in patterns:
        match = re.search(pattern, url)
        if match: return match.group(1)
    return None

def get_youtube_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['hi', 'en'])
        return " ".join([t['text'] for t in transcript_list])
    except: return None

# --- MAIN HANDLER (Sab kuch yahi karega) ---
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # 1. Check API Keys
    gemini_key = os.environ.get("GEMINI_API_KEY")
    resend_key = os.environ.get("RESEND_API_KEY")

    if request.method == 'GET':
        return jsonify({"status": "Online", "message": "All Systems Operational"})

    # 2. Handle POST Requests
    try:
        data = request.json
        action_type = data.get('type') # Pata karo user kya chahta hai (chat, otp, verify)

        # --- A. SEND OTP ---
        if action_type == 'send-otp':
            if not resend_key: return jsonify({"success": False, "error": "Resend Key Missing"})
            email = data.get('email')
            otp = str(random.randint(100000, 999999))
            otp_storage[email] = otp
            
            # Send Email
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={
                    "from": "onboarding@resend.dev",
                    "to": email,
                    "subject": "BotKey OTP Login",
                    "html": f"<strong>Your OTP is: {otp}</strong>"
                }
            )
            if resp.status_code == 200: return jsonify({"success": True})
            else: return jsonify({"success": False, "error": resp.text})

        # --- B. VERIFY OTP ---
        elif action_type == 'verify-otp':
            email = data.get('email')
            user_otp = data.get('otp')
            if otp_storage.get(email) == user_otp:
                del otp_storage[email]
                return jsonify({"success": True})
            return jsonify({"success": False, "error": "Wrong OTP"})

        # --- C. CHAT (DEFAULT) ---
        else:
            user_msg = data.get('question', '')
            if not user_msg: return jsonify({"answer": "Empty message."})

            # YouTube Check
            final_prompt = user_msg
            if "youtube.com" in user_msg or "youtu.be" in user_msg:
                vid = extract_video_id(user_msg)
                if vid:
                    trans = get_youtube_transcript(vid)
                    if trans: final_prompt = f"Video Content: {trans}\n\nUser Question: {user_msg}"

            # Gemini Request (Pro Model)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
            resp = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
            
            if resp.status_code == 200:
                return jsonify({"answer": resp.json()['candidates'][0]['content']['parts'][0]['text']})
            else:
                return jsonify({"answer": "Error from Google: " + resp.text})

    except Exception as e:
        return jsonify({"answer": f"Server Error: {str(e)}", "success": False, "error": str(e)})
        
