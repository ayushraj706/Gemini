from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json
import os
import re
import random

app = Flask(__name__)

# --- OTP STORE (Simple In-Memory for Demo) ---
otp_storage = {}

# --- HELPER: YouTube Logic ---
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

# --- ROUTE: Send OTP (Resend API) ---
@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.json
    email = data.get('email')
    api_key = os.environ.get("RESEND_API_KEY")
    
    if not api_key: return jsonify({"error": "Resend API Key missing in Vercel!"}), 500

    # 1. Generate OTP
    otp = str(random.randint(100000, 999999))
    otp_storage[email] = otp # Store temporary

    # 2. Send Email via Resend
    url = "https://api.resend.com/emails"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "from": "onboarding@resend.dev", # Ya apna domain use karein
        "to": email,
        "subject": "Your BaseKey Login OTP",
        "html": f"<strong>Your OTP is: {otp}</strong>"
    }
    
    resp = requests.post(url, headers=headers, json=payload)
    
    if resp.status_code == 200:
        return jsonify({"success": True, "message": "OTP Sent!"})
    else:
        return jsonify({"success": False, "error": resp.text})

# --- ROUTE: Verify OTP ---
@app.route('/api/verify-otp', methods=['POST'])
def verify_otp():
    data = request.json
    email = data.get('email')
    user_otp = data.get('otp')
    
    if email in otp_storage and otp_storage[email] == user_otp:
        del otp_storage[email] # Clear OTP after use
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "Invalid OTP"})

# --- MAIN CHAT ROUTE (With Auto-Switch Logic) ---
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    
    if request.method == 'POST':
        data = request.json
        user_msg = data.get('question', '')
        
        # YouTube Logic
        final_prompt = user_msg
        if "youtube.com" in user_msg or "youtu.be" in user_msg:
            vid = extract_video_id(user_msg)
            if vid:
                trans = get_youtube_transcript(vid)
                if trans: final_prompt = f"Video Content: {trans}\n\nUser Question: {user_msg}"

        # Gemini Logic (Auto-Switch 1.5 Flash -> Pro)
        models = ["gemini-1.5-flash", "gemini-pro"]
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
            resp = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps({"contents": [{"parts": [{"text": final_prompt}]}]}))
            if resp.status_code == 200:
                return jsonify({"answer": resp.json()['candidates'][0]['content']['parts'][0]['text']})
        
        return jsonify({"answer": "Error: All models busy."})

    return jsonify({"status": "Active"})
