from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# --- FUNCTION 1: Google se pucho "Kon kon se models hain?" ---
def get_available_models(api_key):
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        res = requests.get(url)
        
        if res.status_code == 200:
            all_models = res.json().get('models', [])
            usable_models = []

            # Sirf wo models chuno jo Text Generation (Chat) karte hain
            for m in all_models:
                if "generateContent" in m.get("supportedGenerationMethods", []):
                    usable_models.append(m['name']) # e.g., models/gemini-1.5-flash
            
            # --- PRIORITY LIST (Humein kaunsa pehle chahiye) ---
            # Hum chahte hain ki pehle "Flash" try kare (Fast/Free), fir "Pro"
            priority_order = [
                "models/gemini-1.5-flash", 
                "models/gemini-1.5-flash-001",
                "models/gemini-1.5-pro",
                "models/gemini-pro",
                "models/gemini-1.0-pro"
            ]
            
            # List ko sort karo hamari pasand ke hisab se
            sorted_models = sorted(usable_models, key=lambda x: priority_order.index(x) if x in priority_order else 99)
            return sorted_models
            
    except Exception as e:
        print(f"Error fetching models: {e}")
    
    # Agar list nahi mili, toh ye fallback use karo
    return ["models/gemini-1.5-flash", "models/gemini-pro"]

# --- FUNCTION 2: Message bhejo (Retry System ke sath) ---
def try_generate_content(api_key, user_msg):
    # Step 1: Models ki list mangwao
    model_list = get_available_models(api_key)
    
    last_error = ""

    # Step 2: Ek-ek karke models try karo
    for model_name in model_list:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/{model_name}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": user_msg}]}]}
            headers = {'Content-Type': 'application/json'}

            response = requests.post(url, headers=headers, data=json.dumps(payload))

            # Agar Success (200) hai, toh turant jawab bhej do
            if response.status_code == 200:
                return {
                    "success": True, 
                    "answer": response.json()['candidates'][0]['content']['parts'][0]['text'],
                    "model_used": model_name
                }
            
            # Agar 429 (Limit Khatam) ya 404 (Not Found) hai, toh next model try karo
            else:
                print(f"Model {model_name} failed: {response.status_code}")
                last_error = f"Model {model_name} error: {response.text}"
                continue # Agla model try karo

        except Exception as e:
            last_error = str(e)
            continue

    # Agar saare models fail ho gaye
    return {"success": False, "error": "Saare models busy hain ya limit khatam ho gayi hai. " + last_error}

# --- MAIN ROUTE ---
@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    # 1. API Key Check
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"answer": "Error: API Key missing in Vercel Settings!"})

    # 2. Browser Check
    if request.method == 'GET':
        return jsonify({"status": "Online", "message": "Smart Engine Ready!"})

    # 3. Chat Logic
    try:
        data = request.json
        user_msg = data.get('question', '')

        if not user_msg:
            return jsonify({"answer": "Empty message."})

        # Smart Function Call
        result = try_generate_content(api_key, user_msg)

        if result["success"]:
            # Jawab ke sath model ka naam bhi bhej raha hu (Debugging ke liye)
            return jsonify({"answer": result["answer"]})
        else:
            return jsonify({"answer": f"System Error: {result['error']}"})

    except Exception as e:
        return jsonify({"answer": f"Server Crash: {str(e)}"})
        
