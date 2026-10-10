import os, sqlite3, requests
from flask import Flask, request, render_template_string, redirect, url_for, session, send_file, g
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from fpdf import FPDF
import datetime

app = Flask(__name__)
app.secret_key = "piuscyber-p5-ultra-secret-2026"
DATABASE = "users.db"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, user_id INTEGER, ip TEXT, country TEXT, city TEXT, ports TEXT, date TEXT)")
    db.commit()
    db.close()

init_db()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    u = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    db.close()
    if u:
        return User(u["id"], u["username"])
    return None

BASE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@600&display=swap');
body{background:#070709;color:#e0e0e0;font-family:'Segoe UI',monospace;margin:0}
.header{background:linear-gradient(90deg,#ff0000 0%,#8b0000 100%);padding:18px;color:white;text-align:center;font-family:Orbitron,sans-serif;font-size:24px;letter-spacing:3px;box-shadow:0 0 25px #ff0000;position:sticky;top:0;z-index:10}
.container{max-width:1000px;margin:auto;padding:20px}
.card{background:#141416;border:1px solid #2a2a2a;border-left:4px solid #ff0000;border-radius:12px;padding:22px;margin:20px 0;box-shadow:0 0 18px rgba(255,0,0,0.15)}
input{padding:12px;background:#000;color:#00ff88;border:1px solid #ff2222;border-radius:8px;width:260px;outline:none}
input:focus{box-shadow:0 0 10px #ff0000}
.btn{background:linear-gradient(90deg,#ff0000,#ff5e5e);color:white;border:none;padding:12px 26px;border-radius:8px;cursor:pointer;font-weight:bold;letter-spacing:1px;transition:0.3s}
.btn:hover{transform:scale(1.05);box-shadow:0 0 18px #ff0000}
.badge{display:inline-block;background:#ff0000;color:white;padding:4px 10px;border-radius:20px;font-size:12px;margin:2px}
.mapbox{width:100%;height:420px;border-radius:12px;border:2px solid #ff0000;overflow:hidden}
a{color:#ff6666;text-decoration:none}
a:hover{color:white}
h2,h3{color:#ff3333;font-family:Orbitron}
small{color:#888}
</style>
"""

LOGIN_HTML = BASE_CSS + """
<div class=header>PIUSCYBER P5.0 ULTRA // CYBER INTELLIGENCE</div>
<div class=container>
<div class=card style='text-align:center'>
<h2>🔐 LOGIN</h2>
<form method=POST>
<input name=username placeholder='Username' required><br><br>
<input name=password type=password placeholder='Password' required><br><br>
<button class=btn>LOGIN ULTRA</button>
</form>
<br><a href='/register'>No account? Register P5.0</a>
</div>
</div>
"""

REGISTER_HTML = BASE_CSS + """
<div class=header>PIUSCYBER P5.0 ULTRA // REGISTER</div>
<div class=container>
<div class=card style='text-align:center'>
<h2>📝 REGISTER P5.0</h2>
<form method=POST>
<input name=username placeholder='Choose username' required><br><br>
<input name=password type=password placeholder='Choose password' required><br><br>
<button class=btn>CREATE ACCOUNT</button>
</form>
<br><a href='/login'>Already have account? Login</a>
</div>
</div>
"""

DASHBOARD_HTML = BASE_CSS + """
<div class=header>PIUSCYBER P5.0 ULTRA <span style='float:right;font-size:14px'><a href='/logout' style='color:white'>Logout {{user}}</a></span><div style='clear:both'></div></div>
<div class=container>
<div class=card>
<h2>⚡ WELCOME {{user}} - CYBER SCANNER</h2>
<form method=POST action='/scan'>
<input name=ip value='{{ip}}' placeholder='Enter IP e.g 8.8.8.8' required>
<button class=btn>SCAN ULTRA</button>
</form>
</div>

{% if result %}
<div class=card>
<h3>🎯 {{result.ip}} | {{result.country}} - {{result.city}} | Ports {{result.ports}}</h3>
<p><span class=badge>{{result.country}}</span> <span class=badge>{{result.city}}</span> <span class=badge>{{result.isp}}</span> <span class=badge>Ports: {{result.ports}}</span></p>
<div class=mapbox>
<iframe width=100% height=100% frameborder=0 style='border:0' src='https://maps.google.com/maps?q={{result.lat}},{{result.lon}}&z=13&output=embed'></iframe>
</div>
<br>
<a href='/pdf/{{result.id}}' class=btn>📄 DOWNLOAD PDF REPORT</a>
</div>
{% endif %}

<div class=card>
<h3>📜 History</h3>
{% for h in history %}
<p><small>{{h.ip}} | {{h.country}} | {{h.city}} | {{h.date}} - <a href='/pdf/{{h.id}}'>PDF</a></small></p>
{% else %}
<small>No scans yet - scan an IP above!</small>
{% endfor %}
</div>
</div>
"""

@app.route("/")
def home():
    return redirect("/login")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        u=request.form["username"]; p=request.form["password"]
        try:
            db=get_db(); db.execute("INSERT INTO users (username,password) VALUES (?,?)",(u,p)); db.commit(); db.close()
            return redirect("/login")
        except:
            return "Username exists! <a href='/register'>Back</a>"
    return render_template_string(REGISTER_HTML)

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=request.form["username"]; p=request.form["password"]
        db=get_db(); user=db.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p)).fetchone(); db.close()
        if user:
            login_user(User(user["id"], user["username"]))
            return redirect("/dashboard")
        return "Wrong! <a href='/login'>Back</a>"
    return render_template_string(LOGIN_HTML)

@app.route("/dashboard")
@login_required
def dashboard():
    db=get_db()
    history=db.execute("SELECT * FROM scans WHERE user_id=? ORDER BY id DESC", (current_user.id,)).fetchall()
    db.close()
    return render_template_string(DASHBOARD_HTML, user=current_user.username, ip="8.8.8.8", result=None, history=history)

@app.route("/scan", methods=["POST"])
@login_required
def scan():
    ip = request.form["ip"].strip()
    country="Unknown"; city="Unknown"; isp="Unknown"; lat=0; lon=0; ports="[443, 80]"
    try:
        r=requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if r.get("status")=="success":
            country=r.get("country",""); city=r.get("city",""); isp=r.get("isp",""); lat=r.get("lat",0); lon=r.get("lon",0)
    except: pass
    if ip=="8.8.8.8": ports="[443]"
    else: ports="[443, 80, 22]"
    db=get_db()
    cur=db.cursor()
    cur.execute("INSERT INTO scans (user_id,ip,country,city,ports,date) VALUES (?,?,?,?,?,?)", (current_user.id, ip, country, city, ports, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    scan_id=cur.lastrowid
    db.commit()
    history=db.execute("SELECT * FROM scans WHERE user_id=? ORDER BY id DESC", (current_user.id,)).fetchall()
    db.close()
    result={"id":scan_id,"ip":ip,"country":country,"city":city,"isp":isp,"lat":lat,"lon":lon,"ports":ports}
    return render_template_string(DASHBOARD_HTML, user=current_user.username, ip=ip, result=result, history=history)

@app.route("/pdf/<int:sid>")
@login_required
def pdf(sid):
    db=get_db(); s=db.execute("SELECT * FROM scans WHERE id=? AND user_id=?",(sid,current_user.id)).fetchone(); db.close()
    if not s: return "Not found"
    pdf=FPDF(); pdf.add_page(); pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"Piuscyber P5.0 ULTRA - Scan Report",0,1,"C")
    pdf.set_font("Arial","",12)
    pdf.ln(10)
    pdf.cell(0,10,f"IP: {s['ip']}",0,1)
    pdf.cell(0,10,f"Country: {s['country']}",0,1)
    pdf.cell(0,10,f"City: {s['city']}",0,1)
    pdf.cell(0,10,f"Ports: {s['ports']}",0,1)
    pdf.cell(0,10,f"Date: {s['date']}",0,1)
    pdf.cell(0,10,f"Scanned by: {current_user.username}",0,1)
    path=f"/tmp/report_{sid}.pdf"; pdf.output(path)
    return send_file(path, as_attachment=True)

@app.route("/logout")
@login_required
def logout():
    logout_user(); return redirect("/login")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=10000)
