from flask import Flask, request
import socket

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    ip = ""
    result = ""

    if request.method == "POST":
        ip = request.form.get("ip", "").strip()
        # Auto-fix: 192 168 1 1 -> 192.168.1.1
        ip = ip.replace(" ", ".").replace(",", ".")
        if not ip:
            ip = "8.8.8.8"

        result += f"<div style='background:#000;padding:15px;margin-top:20px;border-radius:10px;text-align:left;border:1px solid #333'>"
        result += f"<h3 style='color:orange'>Scanning {ip}...</h3>"

        try:
            # Validate IP
            socket.inet_aton(ip)
            for port in [80, 8080, 8000, 554, 37777]:
                s = socket.socket()
                s.settimeout(1)
                try:
                    s.connect((ip, port))
                    result += f"<p style='color:red'>[OPEN] Port {port} - EXPOSED!</p>"
                except:
                    result += f"<p style='color:#0f0'>[closed] Port {port} - safe</p>"
                s.close()
            result += "<h3 style='color:#0f0'>SECURE / SCAN COMPLETE</h3>"
        except:
            result += f"<p style='color:orange'>Invalid IP. Use like 8.8.8.8 or 143.105.112.29</p>"

        result += "</div>"

    html = f"""
    <body style="background:#0a0a0a;color:#0f0;font-family:monospace;text-align:center;padding:25px">
    <div style="border:2px solid orange;border-radius:15px;padding:20px;max-width:650px;margin:auto;background:#111">
        <h1 style="color:orange;background:orangered;padding:12px;border-radius:10px;color:black">Piuscyber P4.0 WEB</h1>
        <p>Public IP Camera Scanner</p>
        <p>Your IP: 153.67.70.225 | Lagos, Nigeria</p>
        <form method="POST">
            <input name="ip" value="{ip}" placeholder="143.105.112.29" style="padding:14px;width:80%;border:2px solid orange;border-radius:8px;font-size:16px">
            <br><br>
            <button type="submit" style="padding:14px 30px;background:orange;color:black;font-weight:bold;border:none;border-radius:8px;cursor:pointer;font-size:16px">SCAN NOW - P4.0</button>
        </form>
        {result}
        <p style="font-size:11px;margin-top:25px;color:#888">Built by Piuscyber | github.com/piuscyber/piuscyber-p3.0-pro</p>
    </div>
    </body>
    """
    return html

if __name__ == "__main__":
    print("P4.0 LIVE at http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)