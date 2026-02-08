from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json
import os
import re
import random

app = Flask(__name__)

# --- MEMORY FOR OTP ---
otp_storage = {}

# --- HELPER 1: PROFESSIONAL EMAIL TEMPLATE 🎨 ---
def get_email_template(otp):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0; }}
            .container {{ max-width: 500px; margin: 30px auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1); overflow: hidden; border: 1px solid #e0e0e0; }}
            .header {{ background-color: #2563EB; color: #ffffff; padding: 20px; text-align: center; }}
            .header h1 {{ margin: 0; font-size: 24px; font-weight: 600; letter-spacing: 1px; }}
            .content {{ padding: 30px 20px; text-align: center; }}
            .text {{ color: #333333; font-size: 16px; margin-bottom: 20px; }}
            .otp-box {{ background-color: #f0f7ff; border: 2px dashed #2563EB; border-radius: 8px; padding: 15px; display: inline-block; margin: 10px 0; }}
            .otp-code {{ font-size: 32px; font-weight: bold; color: #2563EB; letter-spacing: 5px; margin: 0; }}
            .footer {{ background-color: #f9f9f9; padding: 15px; text-align: center; color: #888888; font-size: 12px; border-top: 1px solid #eeeeee; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>BaseKey AI</h1>
            </div>
            <div class="content">
                <p class="text">Hello,</p>
                <p class="text">Use the One-Time Password (OTP) below to securely log in to your account.</p>
                
                <div class="otp-box">
                    <p class="otp-code">{otp}</p>
                </div>
                
                <p class="text" style="font-size: 14px; color: #666; margin-top: 20px;">This code is valid for 10 minutes. Do not share it with anyone.</p>
            </div>
            <div class="footer">
                &copy; 2026 BaseKey AI Systems. All rights reserved.<br>
                Secure Login Verification
            </div>
        </div>
    </body>
    </html>
    """

# --- HELPER 2: YOUTUBE & GEMINI LOGIC ---
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

# --- MAIN ROUTE ---
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    resend_key = os.environ.get("RESEND_API_KEY")

    if request.method == 'GET':
        return jsonify({"status": "Online"})

    try:
        data = request.json
        action_type = data.get('type')

        # --- A. SEND OTP (DESIGNED EMAIL) ---
        if action_type == 'send-otp':
            if not resend_key: return jsonify({"success": False, "error": "Resend API Key Missing"})
            email = data.get('email')
            otp = str(random.randint(100000, 999999))
            otp_storage[email] = otp
            
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={
                    "from": "onboarding@resend.dev",
                    "to": email,
                    "subject": "🔐 BaseKey Login Code: " + otp,
                    "html": get_email_template(otp) # Naya Design Call Kiya
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
            return jsonify({"success": False, "error": "Invalid OTP"})

        # --- C. CHAT (SMART MODEL SWITCHING) ---
        else:
            user_msg = data.get('question', '')
            if not user_msg: return jsonify({"answer": "Empty message"})

            final_prompt = user_msg
            if "youtube.com" in user_msg or "youtu.be" in user_msg:
                vid = extract_video_id(user_msg)
                if vid:
                    trans = get_youtube_transcript(vid)
                    if trans: final_prompt = f"Video Content: {trans}\n\nUser Question: {user_msg}"

            # --- MODEL FIX: List of Models to Try ---
            # Agar pehla fail hoga, code apne aap doosra try karega.
            models = ["gemini-1.5-flash", "gemini-pro"]
            
            for model in models:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                    payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
                    resp = requests.post(url, headers={'Content-Type': 'application/json'}, data=json.dumps(payload))
                    
                    if resp.status_code == 200:
                        return jsonify({"answer": resp.json()['candidates'][0]['content']['parts'][0]['text']})
                    else:
                        print(f"Model {model} failed with {resp.status_code}, trying next...")
                        continue # Agla model try karo
                except:
                    continue
            
            return jsonify({"answer": "Error: All models are busy right now. Please try again in 1 min."})

    except Exception as e:
        return jsonify({"answer": "Server Error", "error": str(e)})
        
