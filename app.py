from flask import Flask, request, render_template_string
import socket, requests, datetime

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Piuscyber P4.0 PRO MAX</title>
<style>
body{background:#000;color:#0f0;font-family:monospace;margin:0;padding:15px}
.box{border:2px solid #ff9900;max-width:600px;margin:20px auto;padding:20px;border-radius:10px;box-shadow:0 0 20px #ff9900}
.header{background:#ff9900;color:#000;text-align:center;padding:10px;font-weight:bold;font-size:18px;border-radius:5px}
input{width:90%;padding:12px;margin:10px 0;background:#111;color:#0f0;border:1px solid #ff9900;border-radius:5px}
button{background:#ff9900;color:#000;border:none;padding:12px 25px;font-weight:bold;cursor:pointer;border-radius:5px;width:95%}
button:hover{background:#ffaa22;transform:scale(1.05)}
.result{background:#111;border:1px solid #333;padding:15px;margin-top:15px;border-radius:5px;text-align:left;white-space:pre-wrap}
.green{color:#0f0}.orange{color:#ff9900}.red{color:#ff4444}
.blink{animation:blink 1s infinite}@keyframes blink{50%{opacity:0}}
</style>
</head>
<body>
<div class="box">
<div class="header">⚡ Piuscyber P4.0 PRO MAX ⚡</div>
<p style="text-align:center">Advanced IP Intelligence + Camera Scanner<br><span class="green">Your IP: {{myip}} | {{mycity}}</span> <span class="blink">● LIVE</span></p>

<form method="POST">
<input name="ip" value="{{target}}" placeholder="Enter IP e.g 8.8.8.8" required>
<button type="submit">🔍 SCAN NOW - PRO MAX</button>
</form>

{% if result %}
<div class="result">{{result|safe}}</div>
{% endif %}

<p style="text-align:center;font-size:10px;margin-top:15px">Built by Piuscyber | Ado-Ekiti, Nigeria<br>github.com/piuscyber/piuscyber-p3.0-pro</p>
</div>
</body>
</html>
"""

def get_my_ip():
    try:
        r = requests.get("https://ipinfo.io/json", timeout=5).json()
        return r.get('ip','Unknown'), f"{r.get('city','')}, {r.get('country','')}", r
    except:
        return "Unknown", "Lagos, Nigeria", {}

@app.route("/", methods=["GET","POST"])
def home():
    myip, mycity, _ = get_my_ip()
    target = "143.105.112.29"
    result = ""
    if request.method == "POST":
        target = request.form.get("ip","").strip()
        try:
            # IP Info
            info = requests.get(f"https://ipinfo.io/{target}/json", timeout=5).json()
            city = info.get('city','Unknown')
            country = info.get('country','Unknown')
            org = info.get('org','Unknown')
            loc = info.get('loc','Unknown')
            
            # Port Scan
            open_ports = []
            for p in [80,81,82,83,84,88,8000,8080,554,37777,34567]:
                s = socket.socket()
                s.settimeout(0.6)
                try:
                    s.connect((target, p))
                    open_ports.append(p)
                except: pass
                s.close()
            
            # Banner
            banner = "N/A"
            try:
                s = socket.socket()
                s.settimeout(2)
                s.connect((target, 80))
                s.send(b"HEAD / HTTP/1.0\r\n\r\n")
                banner = s.recv(200).decode(errors='ignore').strip()[:150]
                s.close()
            except: pass

            is_cam = "YES - Possible Camera!" if any(x in open_ports for x in [81,554,37777,34567,88]) else "NO"
            
            result = f"""<span class="orange">========== P4.0 PRO SCAN REPORT ==========</span>
<span class="green">Target:</span> {target}
<span class="green">Time:</span> {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} WAT

<span class="orange">[GEOLOCATION]</span>
City: {city}, {country}
Coordinates: {loc}
ISP/Org: {org}

<span class="orange">[PORTS]</span>
Open Ports: {open_ports if open_ports else 'None (Filtered)'}
Total Open: {len(open_ports)}

<span class="orange">[CAMERA DETECTION]</span>
Camera?: <span class="{'red' if 'YES' in is_cam else 'green'}">{is_cam}</span>

<span class="orange">[BANNER]</span>
{banner}

<span class="orange">[SHODAN / GOOGLE DORK]</span>
Search: https://www.shodan.io/host/{target}
Google: inurl:view.shtml intitle:Network Camera {target}

<span class="green">========== SCAN COMPLETE ==========</span>
"""
        except Exception as e:
            result = f"<span class='red'>Error: {e}</span>"
    
    return render_template_string(HTML, myip=myip, mycity=mycity, target=target, result=result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
