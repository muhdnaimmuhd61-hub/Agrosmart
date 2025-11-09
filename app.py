from flask import Flask, render_template_string, request, redirect, url_for, jsonify, send_file
import sqlite3, csv, io

app = Flask(__name__)
DB_FILE = "agro.db"

# texts
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
    "recommendation": "Recommended Seed for Your Region",
    "download_csv": "Download Farmers CSV"
}

# sample states + LGAs (for full use, replace with full list)
states_lgas = [
    {"state":"Abia","lgas":["Aba North","Aba South","Umuahia North","Umuahia South","Ikwuano","Isiala Ngwa North","Isiala Ngwa South","Isuikwuato","Obi Ngwa","Ohafia","Osisioma","Umu Nneochi"]},
    {"state":"Adamawa","lgas":["Demsa","Fufure","Ganye","Girei","Gombi","Guyuk","Hong","Jada","Lamurde","Madagali","Maiha","Mayo Belwa","Michika","Mubi North","Mubi South","Numan","Shelleng","Song","Toungo","Yola North","Yola South"]},
    # … add all remaining states …
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

# Home
@app.route('/')
def home():
    return render_template_string("""
    <html><head><style>
      body { background-color: #d4edda; font-family: Arial, sans‑serif; padding:20px; }
      .nav a { margin-right:15px; text-decoration:none; color:#155724; font-weight:bold; }
      .btn { background-color:#28a745; color:white; padding:8px 12px; border:none; border-radius:4px; text-decoration:none; }
    </style></head><body>
      <h1>{{title}}</h1>
      <p>{{welcome}}</p>
      <div class="nav">
        <a class="btn" href="{{ url_for('register') }}">{{reg_text}}</a>
        <a class="btn" href="{{ url_for('dashboard') }}">{{dash_text}}</a>
        <a class="btn" href="{{ url_for('weather') }}">{{weather_text}}</a>
      </div>
    </body></html>
    """, title=texts["home_title"], welcome=texts["home_welcome"],
       reg_text=texts["register"], dash_text=texts["dashboard"], weather_text=texts["weather"])

# Register Farmers
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
        c.execute("INSERT INTO farmers(name,state_id,lga_id,crop) VALUES (?,?,?,?)",
                  (name,state_id,lga_id,crop))
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template_string("""
    <html><head><style>
      body { background-color: #d4edda; font-family: Arial, sans‑serif; padding:20px; }
      .btn { background-color:#28a745; color:white; padding:8px 12px; border:none; border-radius:4px; text-decoration:none; }
    </style></head><body>
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
        <select name="lga" id="lga" required><option value="">Select LGA</option></select><br><br>
        {{crop_label}}: <input type="text" name="crop" required><br><br>
        <button class="btn" type="submit">{{submit_text}}</button>
      </form>
      <p><a class="btn" href="{{ url_for('home') }}">{{back_label}}</a></p>

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
                opt.value = l.id; opt.text = l.name;
                lgaSelect.add(opt);
              });
            });
        }
      </script>
    </body></html>
    """, reg_text=texts["register"], name_label=texts["name"], state_label=texts["state"],
       lga_label=texts["lga"], crop_label=texts["crop"], submit_text=texts["submit"], back_label=texts["back_home"],
       states=states)

# API for LGAs
@app.route('/api/lgas')
def api_lgas():
    sid = request.args.get("state_id")
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id,name FROM lgas WHERE state_id=? ORDER BY name", (sid,))
    rows = c.fetchall()
    conn.close()
    return jsonify({"lgas":[{"id":r[0],"name":r[1]} for r in rows]})

# Dashboard + CSV Download
@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
      SELECT s.name, COUNT(f.id) FROM states s
      LEFT JOIN farmers f ON f.state_id = s.id
      GROUP BY s.id
    """)
    data = c.fetchall()
    # recent farmers
    c.execute("""SELECT f.name, s.name, l.name, f.crop
                 FROM farmers f
                 LEFT JOIN states s ON f.state_id=s.id
                 LEFT JOIN lgas l ON f.lga_id=l.id
                 ORDER BY f.id DESC LIMIT 10""")
    recent = c.fetchall()
    conn.close()
    labels = [d[0] for d in data]
    counts = [d[1] for d in data]
    return render_template_string("""
    <html><head><style>
      body { background-color: #d4edda; font-family: Arial, sans‑serif; padding:20px; }
      .btn { background-color:#28a745; color:white; padding:8px 12px; border:none; border-radius:4px; text-decoration:none; }
      table { width:100%; border-collapse: collapse; margin-top:20px; }
      th,td { border:1px solid #ccc; padding:8px; text-align:left; }
      th { background-color:#f8f9fa; }
    </style></head><body>
      <h2>{{dash_text}}</h2>
      <a class="btn" href="{{ url_for('download_csv') }}">{{download_text}}</a>
      <canvas id="chart" width="600" height="300"></canvas>

      <h3>Recent Farmers</h3>
      <table><thead><tr><th>{{name_col}}</th><th>{{state_col}}</th><th>{{lga_col}}</th><th>{{crop_col}}</th></tr></thead><tbody>
        {% for r in recent %}
          <tr><td>{{r[0]}}</td><td>{{r[1]}}</td><td>{{r[2]}}</td><td>{{r[3]}}</td></tr>
        {% endfor %}
      </tbody></table>

      <p><a class="btn" href="{{ url_for('home') }}">{{back_label}}</a> | <a class="btn" href="{{ url_for('register') }}">{{reg_text}}</a></p>

      <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
      <script>
        const ctx = document.getElementById('chart').getContext('2d');
        new Chart(ctx,{
          type:'bar',
          data:{ labels: {{labels|tojson}}, datasets:[{ label:'{{farmers_label}}', data: {{counts|tojson}}, backgroundColor:'rgba(54,162,235,0.5)', borderColor:'rgba(54,162,235,1)', borderWidth:1 }]},
          options:{scales:{y:{beginAtZero:true}}}
        });
      </script>
    </body></html>
    """, dash_text=texts["dashboard"], labels=labels, counts=counts,
       download_text=texts["download_csv"], name_col=texts["name"], state_col=texts["state"],
       lga_col=texts["lga"], crop_col=texts["crop"], back_label=texts["back_home"],
       reg_text=texts["register"], farmers_label=texts["farmers_per_state"])

@app.route('/download_csv')
def download_csv():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""SELECT f.name, s.name, l.name, f.crop
                 FROM farmers f
                 LEFT JOIN states s ON f.state_id=s.id
                 LEFT JOIN lgas l ON f.lga_id=l.id""")
    rows = c.fetchall()
    conn.close()
    si = io.StringIO()
    cw = csv.writer(si)
    cw.writerow([texts["name"], texts["state"], texts["lga"], texts["crop"]])
    for r in rows:
        cw.writerow(r)
    output = io.BytesIO()
    output.write(si.getvalue().encode('utf‑8'))
    output.seek(0)
    return send_file(output, mimetype='text/csv', as_attachment=True, download_name="farmers.csv")

# Weather / Seed Recommendation
@app.route('/weather', methods=['GET','POST'])
def weather():
    recommended = None
    if request.method == "POST":
        state_id = request.form.get("state")
        lga_id = request.form.get("lga")
        # placeholder logic
        recommended = "Maize (High‑yield variety)" if state_id and int(state_id)%2==0 else "Sorghum (Drought tolerant)"
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id,name FROM states ORDER BY name")
    states = c.fetchall()
    conn.close()
    return render_template_string("""
    <html><head><style>
      body { background-color: #d4edda; font-family: Arial, sans‑serif; padding:20px; }
      .btn { background-color:#28a745; color:white; padding:8px 12px; border:none; border-radius:4px; text-decoration:none; }
    </style></head><body>
      <h2>{{weather_text}}</h2>
      <form method="POST">
        {{state_label}}:
        <select name="state" id="state" onchange="fetchLGAs2()" required><option value="">Select State</option>
          {% for id,name in states %}
            <option value="{{id}}">{{name}}</option>
          {% endfor %}
        </select><br><br>
        {{lga_label}}:
        <select name="lga" id="lga" required><option value="">Select LGA</option></select><br><br>
        <button class="btn" type="submit">{{submit_text}}</button>
      </form>
      {% if recommended %}
        <h3>{{recommendation_label}}: <strong>{{recommended}}</strong></h3>
      {% endif %}
      <p><a class="btn" href="{{ url_for('home') }}">{{back_label}}</a></p>

      <script>
        function fetchLGAs2(){
          const sid = document.getElementById("state").value;
          const lgaSelect = document.getElementById("lga");
          lgaSelect.innerHTML="<option value=''>Select LGA</option>";
          fetch('/api/lgas?state_id=' + sid)
            .then(res=>res.json())
            .then(data=>{
              data.lgas.forEach(l => {
                const opt = document.createElement('option');
                opt.value = l.id; opt.text = l.name;
                lgaSelect.add(opt);
              });
            });
        }
      </script>
    </body></html>
    """, weather_text=texts["weather"], state_label=texts["state"], lga_label=texts["lga"],
       submit_text=texts["submit"], recommendation_label=texts["recommendation"], back_label=texts["back_home"],
       states=states, recommended=recommended)

if __name__ == '__main__':
    app.run(debug=True)
