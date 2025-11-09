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

states_lgas = [
    {"state":"Abia","lgas":["Aba North","Aba South","Arochukwu","Bende","Ikwuano","Isiala Ngwa North","Isiala Ngwa South","Isuikwuato","Obi Ngwa","Ohafia","Osisioma","Umuahia North","Umuahia South","Umu Nneochi"]},
    {"state":"Adamawa","lgas":["Demsa","Fufure","Ganye","Girei","Gombi","Guyuk","Hong","Jada","Lamurde","Madagali","Maiha","Mayo Belwa","Michika","Mubi North","Mubi South","Numan","Shelleng","Song","Toungo","Yola North","Yola South"]},
    {"state":"Akwa Ibom","lgas":["Abak","Eastern Obolo","Eket","Esit Eket","Essien Udim","Etim Ekpo","Etinan","Ibeno","Ibesikpo Asutan","Ibiono Ibom","Ikono","Ikot Abasi","Ikot Ekpene","Ini","Itu","Mbo","Mkpat Enin","Nsit Atai","Nsit Ibom","Nsit Ubium","Obot Akara","Okobo","Onna","Oron","Oruk Anam","Udung Uko","Ukanafun","Uruan","Urue-Offong/Oruko","Uyo"]},
    {"state":"Anambra","lgas":["Aguata","Anambra East","Anambra West","Anaocha","Awka North","Awka South","Ayamelum","Dunukofia","Ekwusigo","Idemili North","Idemili South","Ihiala","Njikoka","Nnewi North","Nnewi South","Ogbaru","Onitsha North","Onitsha South","Orumba North","Orumba South","Oyi"]},
    {"state":"Bauchi","lgas":["Bauchi","Bogoro","Damban","Darazo","Dass","Gamawa","Ganjuwa","Giade","Itas/Gadau","Jama’are","Katagum","Kirfi","Misau","Ningi","Shira","Tafawa Balewa","Toro","Warji","Zaki"]},
    {"state":"Bayelsa","lgas":["Brass","Ekeremor","Kolokuma/Opokuma","Nembe","Ogbia","Sagbama","Southern Ijaw","Yenagoa"]},
    {"state":"Benue","lgas":["Ado","Agatu","Apa","Buruku","Gboko","Guma","Gwer East","Gwer West","Katsina-Ala","Konshisha","Kwande","Logo","Makurdi","Obi","Ogbadibo","Ohimini","Oju","Okpokwu","Otukpo","Tarka","Ukum","Vandeikya"]},
    {"state":"Borno","lgas":["Abadam","Askira/Uba","Bama","Bayo","Biu","Chibok","Damboa","Dikwa","Gubio","Guzamala","Gwoza","Hawul","Jere","Kaga","Kala/Balge","Konduga","Kukawa","Kwaya Kusar","Mafa","Magumeri","Maiduguri","Marte","Mobbar","Monguno","Ngala","Nganzai","Shani"]},
    {"state":"Cross River","lgas":["Akpabuyo","Odukpani","Akamkpa","Biase","Abi","Ikom","Obanliku","Obubra","Obudu","Ogoja","Yala","Bekwara","Bakassi","Calabar Municipal","Calabar South","Etung","Boki","Tarkwa Bay"]},
    {"state":"Delta","lgas":["Oshimili North","Oshimili South","Aniocha North","Aniocha South","Ika North East","Ika South","Ndokwa East","Ndokwa West","Isoko North","Isoko South","Okpe","Oshimili South","Sapele","Udu","Ughelli North","Ughelli South","Uvwie","Warri North","Warri South","Warri South West"]},
    {"state":"Ebonyi","lgas":["Abakaliki","Afikpo North","Afikpo South","Ebonyi","Ezza North","Ezza South","Ikwo","Ishielu","Ivo","Izzi","Ohaozara","Ohaukwu","Onicha"]},
    {"state":"Edo","lgas":["Akoko-Edo","Egor","Esan Central","Esan North-East","Esan South-East","Esan West","Etsako Central","Etsako East","Etsako West","Igueben","Ikpoba-Okha","Oredo","Orhionmwon","Ovia North-East","Ovia South-West","Owan East","Owan West","Uhunmwonde"]},
    {"state":"Ekiti","lgas":["Ado","Efon","Ekiti East","Ekiti South-West","Ekiti West","Emure","Gbonyin","Ido-Osi","Ijero","Ikere","Ikole","Ilejemeje","Irepodun/Ifelodun","Ise/Orun","Moba","Oye"]},
    {"state":"Enugu","lgas":["Enugu East","Enugu North","Enugu South","Ezeagu","Igbo Etiti","Igbo Eze North","Igbo Eze South","Isi Uzo","Nkanu East","Nkanu West","Nsukka","Oji River","Udenu","Udi","Uzo Uwani"]},
    {"state":"Gombe","lgas":["Akko","Balanga","Billiri","Dukku","Funakaye","Gombe","Kaltungo","Kwami","Nafada/Bajoga","Shongom","Yamaltu/Deba"]},
    {"state":"Imo","lgas":["Aboh Mbaise","Ahiazu Mbaise","Ehime Mbano","Ezinihitte","Ideato North","Ideato South","Ihitte/Uboma","Ikeduru","Isiala Mbano","Isu","Mbaitoli","Ngor Okpala","Njaba","Nkwerre","Nwangele","Obowo","Oguta","Ohaji/Egbema","Okigwe","Orlu","Orsu","Oru East","Oru West","Owerri Municipal","Owerri North","Owerri West"]},
    {"state":"Jigawa","lgas":["Auyo","Babura","Biriniwa","Birnin Kudu","Buji","Dutse","Gagarawa","Garki","Gumel","Guri","Gwaram","Gwiwa","Hadejia","Jahun","Kafin Hausa","Kaugama","Kazaure","Kiri Kasama","Kiyawa","Maigatari","Malam Madori","Miga","Ringim","Roni","Sule Tankarkar","Taura","Yankwashi"]},
    {"state":"Kaduna","lgas":["Birnin Gwari","Chikun","Giwa","Igabi","Ikara","Jaba","Jema’a","Kachia","Kaduna North","Kaduna South","Kagarko","Kajuru","Kaura","Kauru","Kubau","Kudan","Lere","Makarfi","Sabon Gari","Sanga","Soba","Zangon Kataf","Zaria"]},
    {"state":"Kano","lgas":["Ajingi","Albasu","Bagwai","Bebeji","Bichi","Bunkure","Dala","Dambatta","Dawakin Kudu","Dawakin Tofa","Doguwa","Fagge","Gabasawa","Garko","Garun Mallam","Gaya","Gezawa","Gwale","Gwarzo","Kabo","Kano Municipal","Karaye","Kibiya","Kiru","Kumbotso","Kunchi","Kura","Madobi","Makoda","Minjibir","Nasarawa","Rano","Rimin Gado","Rogo","Shanono","Sumaila","Takai","Tarauni","Tofa","Tsanyawa","Tudun Wada","Ungogo","Warawa","Wudil"]},
    {"state":"Katsina","lgas":["Bakori","Batagarawa","Batsari","Baure","Bindawa","Charanchi","Dandume","Danja","Dan Musa","Daura","Dutsi","Dutsin Ma","Faskari","Funtua","Ingawa","Jibia","Kafur","Kaita","Kankara","Kankia","Katsina","Kurfi","Kusada","Mai’Adua","Malumfashi","Mani","Mashi","Matazu","Musawa","Rimi","Sabuwa","Safana","Sandamu","Zango"]},
    {"state":"Kebbi","lgas":["Aleiro","Arewa Dandi","Argungu","Augie","Bagudo","Birnin Kebbi","Bunza","Dandi","Fakai","Gwandu","Jega","Kalgo","Koko/Besse","Maiyama","Ngaski","Sakaba","Shanga","Suru","Wasagu/Danko","Yauri","Zuru"]},
    {"state":"Kogi","lgas":["Adavi","Ajaokuta","Ankpa","Bassa","Dekina","Ibaji","Idah","Ijumu","Kabba/Bunu","Kogi","Lokoja","Mopa-Muro","Ofu","Ogori/Magongo","Okehi","Okene","Olamaboro","Omala","Yagba East","Yagba West"]},
    {"state":"Kwara","lgas":["Asa","Baruten","Edu","Ekiti","Ifelodun","Ilorin East","Ilorin South","Ilorin West","Irepodun","Isin","Kaiama","Moro","Offa","Oke Ero","Oyun","Pategi"]},
    {"state":"Lagos","lgas":["Agege","Ajeromi-Ifelodun","Alimosho","Amuwo-Odofin","Apapa","Badagry","Epe","Eti-Osa","Ibeju-Lekki","Ifako-Ijaiye","Ikeja","Ikorodu","Kosofe","Lagos Island","Lagos Mainland","Mushin","Ojo","Oshodi-Isolo","Shomolu","Surulere"]},
    {"state":"Nasarawa","lgas":["Akwanga","Awe","Doma","Karu","Keana","Keffi","Kokona","Lafia","Nasarawa","Nasarawa Egon","Obi","Toto","Wamba"]},
    {"state":"Niger","lgas":["Agaie","Agwara","Bida","Borgu","Bosso","Chanchaga","Edati","Gbako","Gurara","Katcha","Kontagora","Lapai","Lavun","Magama","Mariga","Mashegu","Mokwa","Muya","Paikoro","Rafi","Rijau","Shiroro","Suleja","Tafa","Wushishi"]},
    {"state":"Ogun","lgas":["Abeokuta North","Abeokuta South","Ado-Odo/Ota","Egbado North","Egbado South","Ewekoro","Ifo","Ijebu East","Ijebu North","Ijebu North East","Ijebu Ode","Ikenne","Imeko Afon","Ipokia","Obafemi-Owode","Odogbolu","Ogun Waterside","Remo North","Shagamu"]},
    {"state":"Ondo","lgas":["Akoko North-East","Akoko North-West","Akoko South-East","Akoko South-West","Akure North","Akure South","Ese Odo","Idanre","Ifedore","Ilaje","Ile Oluji/Okeigbo","Irele","Odigbo","Okitipupa","Ondo East","Ondo West","Ose","Owo"]},
    {"state":"Osun","lgas":["Aiyedaade","Aiyedire","Atakumosa East","Atakumosa West","Boluwaduro","Boripe","Ede North","Ede South","Egbedore","Ejigbo","Ife Central","Ife East","Ife North","Ife South","Ifedayo","Ifelodun","Ila","Ilesa East","Ilesa West","Irepodun","Irewole","Isokan","Iwo","Obokun","Odo Otin","Ola Oluwa","Olorunda","Oriade","Orolu","Osogbo"]},
    {"state":"Oyo","lgas":["Afijio","Akinyele","Atiba","Atisbo","Egbeda","Ibadan North","Ibadan North-East","Ibadan North-West","Ibadan South-East","Ibadan South-West","Ibarapa Central","Ibarapa East","Ibarapa North","Ido","Irepo","Iseyin","Itesiwaju","Iwajowa","Kajola","Lagelu","Ogbomosho North","Ogbomosho South","Ogo Oluwa","Olorunsogo","Oluyole","Ona Ara","Orelope","Ori Ire","Oyo","Oyo East","Saki East","Saki West","Surulere"]},
    {"state":"Plateau","lgas":["Barkin Ladi","Bassa","Bokkos","Jos East","Jos North","Jos South","Kanam","Kanke","Langtang North","Langtang South","Mangu","Mikang","Pankshin","Qua’an Pan","Riyom","Shendam","Wase"]},
    {"state":"Rivers","lgas":["Abua/Odual","Ahoada East","Ahoada West","Akuku-Toru","Andoni","Asari-Toru","Bonny","Degema","Eleme","Emohua","Etche","Gokana","Ikwerre","Khana","Obio/Akpor","Ogba/Egbema/Ndoni","Ogu/Bolo","Okrika","Omuma","Opobo/Nkoro","Oyigbo","Port Harcourt","Tai"]},
    {"state":"Sokoto","lgas":["Binji","Bodinga","Dange Shuni","Gada","Goronyo","Gudu","Gwadabawa","Illela","Isa","Kebbe","Kware","Rabah","Sabon Birni","Shagari","Silame","Sokoto North","Sokoto South","Tambuwal","Tangaza","Tureta","Wamako","Wurno","Yabo"]},
    {"state":"Taraba","lgas":["Ardo Kola","Bali","Donga","Gashaka","Gassol","Ibi","Jalingo","Karim Lamido","Kumi","Lau","Sardauna","Takum","Ussa","Wukari","Yorro","Zing"]},
    {"state":"Yobe","lgas":["Bade","Bursari","Damaturu","Fika","Fune","Geidam","Gujba","Gulani","Jakusko","Karasuwa","Machina","Nangere","Nguru","Potiskum","Tarmuwa","Yunusari","Yusufari"]},
    {"state":"Zamfara","lgas":["Anka","Bakura","Birnin Magaji/Kiyaw","Bukkuyum","Bungudu","Gummi","Gusau","Kaura Namoda","Maradun","Maru","Shinkafi","Talata Mafara","Chafe","Zurmi"]}

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
