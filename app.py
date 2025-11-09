from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import sqlite3
from pathlib import Path

app = Flask(__name__)
DB_FILE = "agro.db"

# Language texts (English only for now)
texts = {
    "home_title": "🌾 AgroSmart App",
    "home_welcome": "Welcome to AgroSmart App",
    "register": "Register Farmers",
    "dashboard": "Dashboard",
    "weather": "Weather & Seed Recommendation",
    "name": "Name",
    "state": "State",
    "lga": "LGA",
    "crop": "Crop",
    "submit": "Submit",
    "back_home": "Back Home",
    "farmers_per_state": "Farmers per State",
    "recommendation": "Recommended Seed for Your Region"
}

# Full list of states + LGAs (fetch from JSON gist)  
states_lgas = [
    # Example entries:
    {"state": "Abia", "lgas": ["Aba North","Aba South","Umuahia North","Umuahia South","Ikwuano","Isiala Ngwa North","Isiala Ngwa South","Isuikwuato","Obi Ngwa","Ohafia","Osisioma","Umu Nneochi"]},
    {"state": "Adamawa", "lgas": ["Demsa","Fufure","Ganye","Girei","Gombi","Guyuk","Hong","Jada","Lamurde","Madagali","Maiha","Mayo Belwa","Michika","Mubi North","Mubi South","Numan","Shelleng","Song","Toungo","Yola North","Yola South"]},
    # … add all remaining 34 states with their LGAs …
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS states (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL)""")
    c.execute("""CREATE TABLE IF NOT EXISTS lgas (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, state_id INTEGER NOT NULL, FOREIGN KEY(state_id) REFERENCES states(id))""")
    c.execute("""CREATE TABLE IF NOT EXISTS farmers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, state_id INTEGER, lga_id INTEGER, crop TEXT, FOREIGN KEY(state_id) REFERENCES states(id), FOREIGN KEY(lga_id) REFERENCES lgas(id))""")
    conn.commit()

    c.execute("SELECT COUNT(*) FROM states")
    if c.fetchone()[0] == 0:
        for st in states_lgas:
            c.execute("INSERT OR IGNORE INTO states(name) VALUES (?)", (st["state"],))
            conn.commit()
            c.execute("SELECT id FROM states WHERE name=?", (st["state"],))
            sid = c.fetchone()[0]
            for lga in st["lgas"]:
                c.execute("INSERT INTO lgas(name, state_id) VALUES (?,?)", (lga, sid))
        conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template_string("""
    <h1>{{title}}</h1>
    <p>{{welcome}}</p>
    <p><a href="{{ url_for('register') }}">{{reg_text}}</a> | <a href="{{ url_for('dashboard') }}">{{dash_text}}</a> | <a href="{{ url_for('weather') }}">{{weather_text}}</a></p>
    """, title=texts["home_title"], welcome=texts["home_welcome"],
    reg_text=texts["register"], dash_text=texts["dashboard"], weather_text=texts["weather"])

@app.route('/register', methods=['GET','POST'])
def register():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name FROM states ORDER BY name")
    states = c.fetchall()
    if request.method == "POST":
        name = request.form.get("name")
        state_id = request.form.get("state")
        lga_id = request.form.get("lga")
        crop = request.form.get("crop")
        c.execute("INSERT INTO farmers(name, state_id, lga_id, crop) VALUES (?,?,?,?)",
                  (name, state_id, lga_id, crop))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template_string("""
    <h2>{{reg_text}}</h2>
    <form method="POST">
      {{name_label}}: <input type="text" name="name" required><br><br>
      {{state_label}}:
      <select name="state" id="state" onchange="fetchLGAs()" required>
        <option value="">Select State</option>
        {% for id,name in states %}
          <option value="{{id}}">{{name}}</option>
        {% endfor %}
      </select><br><br>
      {{lga_label}}:
      <select name="lga" id="lga" required>
        <option value="">Select LGA</option>
      </select><br><br>
      {{crop_label}}: <input type="text" name="crop" required><br><br>
      <button type="submit">{{submit_text}}</button>
    </form>
    <p><a href="{{ url_for('home') }}">{{back_label}}</a></p>

    <script>
    function fetchLGAs(){
      const sid = document.getElementById("state").value;
      const lgaSelect = document.getElementById("lga");
      lgaSelect.innerHTML = "<option value=''>Select LGA</option>";
      fetch('/api/lgas?state_id=' + sid)
        .then(res=>res.json())
        .then(data=>{
          data.lgas.forEach(l => {
            const opt = document.createElement("option");
            opt.value = l.id;
            opt.text = l.name;
            lgaSelect.add(opt);
          });
        });
    }
    </script>
    """, reg_text=texts["register"], name_label=texts["name"], state_label=texts["state"],
    lga_label=texts["lga"], crop_label=texts["crop"], submit_text=texts["submit"], back_label=texts["back_home"],
    states=states)

@app.route('/api/lgas')
def api_lgas():
    sid = request.args.get("state_id")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name FROM lgas WHERE state_id=? ORDER BY name", (sid,))
    rows = c.fetchall()
    conn.close()
    return jsonify({"lgas":[{"id":r[0],"name":r[1]} for r in rows]})

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
      SELECT s.name, COUNT(f.id)
      FROM states s
      LEFT JOIN farmers f ON f.state_id = s.id
      GROUP BY s.id
    """)
    data = c.fetchall()
    conn.close()
    labels = [d[0] for d in data]
    counts = [d[1] for d in data]
    return render_template_string("""
    <h2>{{dash_text}}</h2>
    <canvas id="chart" width="600" height="300"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>
    const ctx = document.getElementById('chart').getContext('2d');
    new Chart(ctx, {
      type:'bar',
      data:{
        labels: {{labels|tojson}},
        datasets:[{
          label:'{{farmers_label}}',
          data: {{counts|tojson}},
          backgroundColor:'rgba(54,162,235,0.5)',
          borderColor:'rgba(54,162,235,1)',
          borderWidth:1
        }]
      },
      options:{scales:{y:{beginAtZero:true}}}
    });
    </script>
    <p><a href="{{ url_for('home') }}">{{back_label}}</a> | <a href="{{ url_for('register') }}">{{reg_text}}</a></p>
    """, dash_text=texts["dashboard"], labels=labels, counts=counts,
    farmers_label=texts["farmers_per_state"], back_label=texts["back_home"], reg_text=texts["register"])

@app.route('/weather', methods=['GET','POST'])
def weather():
    recommended = None
    if request.method == "POST":
        state_id = request.form.get("state")
        lga_id = request.form.get("lga")
        # Placeholder logic for seed recommendation
        # You can replace with real weather API + agronomy logic
        recommended = "Maize (High-yield variety)" if state_id and int(state_id)%2==0 else "Sorghum (Drought tolerant)"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id, name FROM states ORDER BY name")
    states = c.fetchall()
    conn.close()
    return render_template_string("""
    <h2>{{weather_text}}</h2>
    <form method="POST">
      {{state_label}}:
      <select name="state" id="state" onchange="fetchLGAs()" required>
        <option value="">Select State</option>
        {% for id,name in states %}
          <option value="{{id}}">{{name}}</option>
        {% endfor %}
      </select><br><br>
      {{lga_label}}:
      <select name="lga" id="lga" required>
        <option value="">Select LGA</option>
      </select><br><br>
      <button type="submit">{{submit_text}}</button>
    </form>
    {% if recommended %}
      <h3>{{recommendation_label}}: <strong>{{recommended}}</strong></h3>
    {% endif %}
    <p><a href="{{ url_for('home') }}">{{back_label}}</a></p>

    <script>
    function fetchLGAs(){
      const sid = document.getElementById("state").value;
      const lgaSelect = document.getElementById("lga");
      lgaSelect.innerHTML = "<option value=''>Select LGA</option>";
      fetch('/api/lgas?state_id=' + sid)
        .then(res=>res.json())
        .then(data=>{
          data.lgas.forEach(l => {
            const opt = document.createElement("option");
            opt.value = l.id;
            opt.text = l.name;
            lgaSelect.add(opt);
          });
        });
    }
    </script>
    """, weather_text=texts["weather"], state_label=texts["state"], lga_label=texts["lga"],
    submit_text=texts["submit"], recommendation_label=texts["recommendation"],
    back_label=texts["back_home"], states=states, recommended=recommended)

if __name__ == '__main__':
    app.run(debug=True)
