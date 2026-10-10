from flask import Flask, request, redirect, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import requests, socket, sqlite3, datetime, io
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF

app = Flask(__name__)
app.secret_key = "pius-ultra-2026-ado-ekiti"
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

def init_db():
    conn = sqlite3.connect('p5.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY, user_id INTEGER, ip TEXT, country TEXT, city TEXT, isp TEXT, date TEXT)')
    conn.commit()
    conn.close()
init_db()

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect('p5.db')
    c = conn.cursor()
    c.execute("SELECT id, username FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    conn.close()
    if u:
        return User(u[0], u[1])
    return None

def scan_ip(ip):
    try:
        geo = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        open_ports = []
        for p in [80,443,22,554,8080]:
            s = socket.socket()
            s.settimeout(0.5)
            if s.connect_ex((ip, p)) == 0:
                open_ports.append(p)
            s.close()
        return {"ip": ip, "country": geo.get('country','N/A'), "city": geo.get('city','N/A'), "isp": geo.get('isp','N/A'), "lat": geo.get('lat', 7.6), "lon": geo.get('lon', 5.2), "ports": open_ports}
    except:
        return None

@app.route('/')
def home():
    return '<h1>Piuscyber P5.0 ULTRA</h1><p>Login + DB + Map + PDF</p><a href="/register">Register</a> | <a href="/login">Login</a> | <a href="/dashboard">Dashboard</a>'

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        u = request.form['username']
        p = generate_password_hash(request.form['password'])
        try:
            conn = sqlite3.connect('p5.db')
            conn.execute("INSERT INTO users (username,password) VALUES (?,?)", (u,p))
            conn.commit()
            conn.close()
            return redirect('/login')
        except:
            flash("Username exists")
    return '<h2>Register P5.0</h2><form method="POST"><input name="username" required><input name="password" type="password" required><button>Register</button></form>'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        u = request.form['username']
        pw = request.form['password']
        conn = sqlite3.connect('p5.db')
        c = conn.cursor()
        c.execute("SELECT id,username,password FROM users WHERE username=?", (u,))
        row = c.fetchone()
        conn.close()
        if row and check_password_hash(row[2], pw):
            login_user(User(row[0], row[1]))
            return redirect('/dashboard')
        flash("Wrong login")
    return '<h2>Login P5.0</h2><form method="POST"><input name="username" required><input name="password" type="password" required><button>Login</button></form>'

@app.route('/dashboard', methods=['GET','POST'])
@login_required
def dashboard():
    result = None
    if request.method == 'POST':
        ip = request.form['ip']
        result = scan_ip(ip)
        if result:
            conn = sqlite3.connect('p5.db')
            conn.execute("INSERT INTO scans (user_id,ip,country,city,isp,date) VALUES (?,?,?,?,?,?)", (current_user.id, result['ip'], result['country'], result['city'], result['isp'], str(datetime.datetime.now())[:19]))
            conn.commit()
            conn.close()
    conn = sqlite3.connect('p5.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE user_id=? ORDER BY id DESC", (current_user.id,))
    hist = c.fetchall()
    conn.close()
    html = f'<h1>Welcome {current_user.username}</h1><a href="/logout">Logout</a><hr><form method="POST"><input name="ip" placeholder="8.8.8.8" required><button>SCAN ULTRA</button></form>'
    if result:
        html += f'<h3>{result["ip"]} | {result["country"]} - {result["city"]} | Ports {result["ports"]}</h3><iframe width="100%" height="300" src="https://maps.google.com/maps?q={result["lat"]},{result["lon"]}&z=14&output=embed"></iframe>'
    html += "<hr><h3>History</h3>"
    for h in hist:
        html += f"<p>{h[2]} | {h[3]} | {h[4]} | {h[6]} - <a href='/report/{h[0]}'>PDF</a></p>"
    return html

@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

@app.route('/report/<int:scan_id>')
@login_required
def report(scan_id):
    conn = sqlite3.connect('p5.db')
    c = conn.cursor()
    c.execute("SELECT * FROM scans WHERE id=?", (scan_id,))
    s = c.fetchone()
    conn.close()
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"Piuscyber P5.0 ULTRA Report",ln=True,align='C')
    pdf.set_font("Arial","",12)
    pdf.ln(10)
    pdf.cell(0,10,f"IP: {s[2]}",ln=True)
    pdf.cell(0,10,f"Country: {s[3]}",ln=True)
    pdf.cell(0,10,f"City: {s[4]}",ln=True)
    pdf.cell(0,10,f"ISP: {s[5]}",ln=True)
    pdf.cell(0,10,f"Date: {s[6]}",ln=True)
    out = pdf.output(dest='S').encode('latin-1')
    return send_file(io.BytesIO(out), download_name=f"P5_Report_{s[2]}.pdf", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
