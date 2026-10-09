import socket
import tkinter as tk
from tkinter import scrolledtext
import requests
import threading

# Piuscyber P3.1 PRO MAX - Ado-Ekiti
PORTS = [80,81,82,83,84,88,8000,8008,8080,8081,8082,8443,554,1935,37777,34567,5000]

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

def get_public_ip():
    try:
        return requests.get("https://api.ipify.org", timeout=5).text
    except:
        return "No Internet"

def scan_ip(ip, output_box):
    output_box.delete(1.0, tk.END)
    output_box.insert(tk.END, f"Scanning {ip} for 17 camera ports...\n\n")
    open_ports = []
    for port in PORTS:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.5)
        try:
            sock.connect((ip, port))
            msg = f"[OPEN] {port} - Possible camera/webcam!\n"
            open_ports.append(port)
        except:
            msg = f"[closed] {port}\n"
        output_box.insert(tk.END, msg)
        output_box.see(tk.END)
        sock.close()

    output_box.insert(tk.END, f"\n--- RESULT ---\n")
    if open_ports:
        output_box.insert(tk.END, f"⚠️ {len(open_ports)} open ports! Risky!\nPorts: {open_ports}\n")
    else:
        output_box.insert(tk.END, "✅ SECURE - No camera ports open\n")

    # Shodan Check
    shodan_key = shodan_entry.get().strip()
    pub_ip = public_label.cget("text").split(": ")[1]
    if shodan_key:
        output_box.insert(tk.END, f"\nChecking Shodan for {pub_ip}...\n")
        try:
            r = requests.get(f"https://api.shodan.io/shodan/host/{pub_ip}?key={shodan_key}", timeout=10)
            if r.status_code == 200:
                data = r.json()
                output_box.insert(tk.END, f"Shodan Found: {len(data.get('ports', []))} ports exposed publicly!\n{data.get('ports', [])}\n")
            else:
                output_box.insert(tk.END, f"Shodan: {r.text[:100]}\n")
        except Exception as e:
            output_box.insert(tk.END, f"Shodan error: {e}\n")

    with open("report_P3.1.txt", "w") as f:
        f.write(output_box.get(1.0, tk.END))
    output_box.insert(tk.END, "\nReport saved to report_P3.1.txt")

def start_scan():
    ip = ip_entry.get().strip()
    threading.Thread(target=scan_ip, args=(ip, output_box)).start()

# GUI
root = tk.Tk()
root.title("Piuscyber P3.1 PRO MAX ULTRA")
root.geometry("550x600")

tk.Label(root, text="Piuscyber P3.1 - Camera Exposure Checker", font=("Arial", 14, "bold"), bg="orange").pack(fill="x")

local_ip = get_local_ip()
public_ip = get_public_ip()

local_label = tk.Label(root, text=f"Local IP: {local_ip} (Auto)")
local_label.pack()
public_label = tk.Label(root, text=f"Public IP: {public_ip}")
public_label.pack()

tk.Label(root, text="Target IP to scan:").pack()
ip_entry = tk.Entry(root, width=30)
ip_entry.insert(0, local_ip)
ip_entry.pack()

tk.Label(root, text="Shodan API Key (optional - get free at shodan.io):").pack()
shodan_entry = tk.Entry(root, width=40)
shodan_entry.pack()

tk.Button(root, text="SCAN NOW - PRO MAX", command=start_scan, bg="black", fg="white", font=("Arial", 12, "bold")).pack(pady=10)

output_box = scrolledtext.ScrolledText(root, height=25)
output_box.pack(fill="both", expand=True)

root.mainloop()