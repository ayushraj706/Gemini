from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return jsonify({"answer": "Congratulations! Server is Working. Ab hum main code daal sakte hain."})

def handler(request):
    return app(request)
    
