import tkinter as tk
from tkinter import ttk
import socket
import threading
import requests

# PIUSCYBER P3.2 - PRO MAX PLUS - Ado-Ekiti to World
CAMERA_PORTS = [80, 81, 82, 83, 84, 88, 8000, 8080, 8081, 8090, 554, 1935, 8554, 5000, 7001, 9000, 37777]

def get_ips():
    try:
        local = socket.gethostbyname(socket.gethostname())
    except:
        local = "127.0.0.1"
    try:
        public = requests.get("https://api.ipify.org", timeout=5).text
    except:
        public = "No Internet"
    return local, public

def check_shodan(ip, log_box):
    log_box.insert(tk.END, f"\n[SHODAN] Checking {ip} on internet...\n")
    try:
        # Public Shodan search without API (safe info)
        r = requests.get(f"https://internetdb.shodan.io/{ip}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            ports = data.get('ports', [])
            log_box.insert(tk.END, f"[SHODAN] Open ports found on internet: {ports}\n")
            if any(p in CAMERA_PORTS for p in ports):
                log_box.insert(tk.END, "⚠️ WARNING: Camera port exposed on PUBLIC internet!\n")
            else:
                log_box.insert(tk.END, "✅ No camera ports exposed on public internet.\n")
        else:
            log_box.insert(tk.END, "[SHODAN] No public data or IP private.\n")
    except Exception as e:
        log_box.insert(tk.END, f"[SHODAN] Error: {e}\n")

def scan_target():
    target = ip_entry.get().strip()
    if not target:
        log_box.insert(tk.END, "Enter IP abeg!\n")
        return
    scan_btn.config(state='disabled')
    log_box.delete(1.0, tk.END)
    log_box.insert(tk.END, f"Scanning {target} for {len(CAMERA_PORTS)} camera ports...\n")

    open_found = []
    def do_scan():
        for port in CAMERA_PORTS:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                s.connect((target, port))
                log_box.insert(tk.END, f"[OPEN] {port} -> RISKY!\n")
                open_found.append(port)
            except:
                log_box.insert(tk.END, f"[closed] {port}\n")
            s.close()
            log_box.see(tk.END)

        log_box.insert(tk.END, "\n--- RESULT ---\n")
        if open_found:
            log_box.insert(tk.END, f"🚨 EXPOSED! Open camera ports: {open_found}\n")
        else:
            log_box.insert(tk.END, "✅ SECURE - No camera ports open on target\n")

        # Auto Shodan check if target is public IP
        if target.count('.') == 3 and not target.startswith('192.') and not target.startswith('172.') and not target.startswith('10.'):
            check_shodan(target, log_box)

        # Save report
        with open(f"report_P3.2_{target.replace('.', '_')}.txt", "w") as f:
            f.write(log_box.get(1.0, tk.END))

        scan_btn.config(state='normal')

    threading.Thread(target=do_scan, daemon=True).start()

# GUI
root = tk.Tk()
root.title("Piuscyber P3.2 PRO MAX PLUS - Any IP Scanner + Shodan")
root.geometry("650x600")

local_ip, public_ip = get_ips()

tk.Label(root, text="Piuscyber P3.2 - Any IP + Shodan Intel", font=("Arial", 14, "bold"), bg="orange", fg="black").pack(fill=tk.X, pady=5)
tk.Label(root, text=f"Your Local: {local_ip} | Your Public: {public_ip}", font=("Arial", 9)).pack()

frame = tk.Frame(root)
frame.pack(pady=10)
tk.Label(frame, text="Target IP:").pack(side=tk.LEFT)
ip_entry = tk.Entry(frame, width=25, font=("Arial", 11))
ip_entry.insert(0, local_ip)
ip_entry.pack(side=tk.LEFT, padx=5)
ttk.Button(frame, text="Use My Public IP", command=lambda: [ip_entry.delete(0, tk.END), ip_entry.insert(0, public_ip)]).pack(side=tk.LEFT)

scan_btn = tk.Button(root, text="SCAN NOW - P3.2 PRO", bg="black", fg="orange", font=("Arial", 12, "bold"), command=scan_target)
scan_btn.pack(pady=10)

log_box = tk.Text(root, height=25, bg="black", fg="lime", font=("Consolas", 9))
log_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

root.mainloop()