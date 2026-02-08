from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
import requests
import json
import os
import re
import random

app = Flask(__name__)

otp_storage = {}

# --- 1. EMAIL DESIGN ---
def get_email_template(otp):
    return f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: sans-serif; background: #f4f4f4; padding: 20px;">
        <div style="max-width: 500px; margin: auto; background: #fff; padding: 30px; border-radius: 10px; border: 1px solid #ddd; text-align: center;">
            <h1 style="color: #2563EB; margin: 0;">BaseKey AI</h1>
            <p style="color: #555;">Secure Login Verification</p>
            <div style="background: #eef6ff; padding: 15px; border: 2px dashed #2563EB; border-radius: 8px; display: inline-block; margin: 20px 0;">
                <span style="font-size: 32px; font-weight: bold; color: #2563EB; letter-spacing: 5px;">{otp}</span>
            </div>
            <p style="font-size: 12px; color: #888;">Do not share this code.</p>
        </div>
    </body>
    </html>
    """

# --- 2. HELPERS ---
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

# --- 3. SMART MODEL FINDER (Ye hai naya Jaadoo) ---
def get_best_working_model(api_key):
    # Google se pucho: "Tere paas kaunse models hain?"
    url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            # Hum sirf wo models lenge jo 'generateContent' support karte hain
            # Aur hum 'gemini' wale models ko priority denge
            available_models = []
            for m in data.get('models', []):
                if 'generateContent' in m.get('supportedGenerationMethods', []):
                    name = m['name'].replace('models/', '') # Name saaf karo
                    available_models.append(name)
            
            # Priority List: Flash (Fast/Free) -> Pro (Stable) -> Others
            priority = ['gemini-1.5-flash', 'gemini-1.5-flash-latest', 'gemini-pro', 'gemini-1.0-pro']
            
            # List ko sort karo hamari pasand ke hisab se
            available_models.sort(key=lambda x: priority.index(x) if x in priority else 99)
            return available_models
    except:
        pass
    
    # Agar Google ki list API fail ho jaye, to ye backup list use karo
    return ["gemini-1.5-flash", "gemini-pro", "gemini-1.5-pro-latest"]

# --- MAIN ROUTE ---
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    gemini_key = os.environ.get("GEMINI_API_KEY")
    resend_key = os.environ.get("RESEND_API_KEY")

    if request.method == 'GET':
        return jsonify({"status": "Online", "message": "Auto-Model Engine Ready"})

    try:
        data = request.json
        action_type = data.get('type')

        # --- OTP LOGIC ---
        if action_type == 'send-otp':
            if not resend_key: return jsonify({"success": False, "error": "Resend Key Missing"})
            email = data.get('email')
            otp = str(random.randint(100000, 999999))
            otp_storage[email] = otp
            
            # Note: "from" mein apna verified domain use karein
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {resend_key}", "Content-Type": "application/json"},
                json={
                    "from": "BaseKey Security <login@ayus.fun>", 
                    "to": email,
                    "subject": f"🔐 Login Code: {otp}",
                    "html": get_email_template(otp)
                }
            )
            return jsonify({"success": True} if resp.status_code == 200 else {"success": False, "error": resp.text})

        elif action_type == 'verify-otp':
            email = data.get('email')
            if otp_storage.get(email) == data.get('otp'):
                del otp_storage[email]
                return jsonify({"success": True})
            return jsonify({"success": False, "error": "Invalid OTP"})

        # --- CHAT LOGIC (SMART) ---
        else:
            user_msg = data.get('question', '')
            final_prompt = user_msg
            
            # YouTube Check
            if "youtube.com" in user_msg or "youtu.be" in user_msg:
                vid = extract_video_id(user_msg)
                if vid:
                    trans = get_youtube_transcript(vid)
                    if trans: final_prompt = f"Video Content: {trans}\n\nUser Question: {user_msg}"

            # Step 1: Models ki list mangwao
            model_list = get_best_working_model(gemini_key)
            last_error = ""

            # Step 2: Ek-ek karke try karo
            for model in model_list:
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
                    payload = {"contents": [{"parts": [{"text": final_prompt}]}]}
                    headers = {'Content-Type': 'application/json'}
                    
                    resp = requests.post(url, headers=headers, data=json.dumps(payload))
                    
                    if resp.status_code == 200:
                        # Jawab mil gaya! Bhej do.
                        return jsonify({"answer": resp.json()['candidates'][0]['content']['parts'][0]['text']})
                    else:
                        # Is model ne dhokha diya, error note karo aur agla try karo
                        error_detail = resp.json().get('error', {}).get('message', resp.text)
                        last_error = f"Model {model} failed: {error_detail}"
                        continue 
                except Exception as e:
                    last_error = str(e)
                    continue

            # Agar saare fail ho gaye, to ASLI ERROR dikhao (Generic nahi)
            return jsonify({"answer": f"System Error: {last_error}. (Check API Key or Limits)"})

    except Exception as e:
        return jsonify({"answer": "Critical Server Error", "error": str(e)})
