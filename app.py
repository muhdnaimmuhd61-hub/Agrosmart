from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>🌾 AgroSmart App Live!</h1><p>Welcome to your deployed Flask app.</p>"
