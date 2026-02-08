from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return jsonify({
        "status": "Success",
        "message": "Bhai Flask kaam kar raha hai! Galti Gemini code me thi."
    })

# Vercel Handler
def handler(request):
    return app(request)
    
