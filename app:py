from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    return render_template_string("""
        <h1 style='text-align:center;color:green;'>🌾 AgroSmart App</h1>
        <p style='text-align:center;'>Welcome to your Flask web app deployed from GitHub & Render!</p>
    """)

if __name__ == '__main__':
    app.run(debug=True)
