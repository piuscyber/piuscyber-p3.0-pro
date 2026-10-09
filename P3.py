# Piuscyber p3.0 - Secure Cam Checker (Ethical Version)
# For checking YOUR OWN cameras only
import socket
import requests

print("=== Piuscyber p3.0 Secure-Cam Checker ===")
print("This tool checks YOUR OWN local camera only\n")

target = input("Enter YOUR camera IP (e.g 192.168.43.1 or 127.0.0.1): ").strip()
port = int(input("Enter port [80, 8080, 554]: ") or 80)

# 1. Check if port open
print(f"\n[*] Checking {target}:{port}...")
s = socket.socket()
s.settimeout(3)
try:
    s.connect((target, port))
    print(f"[+] Port {port} OPEN - camera dey reachable")
    s.close()
except:
    print(f"[-] Port {port} CLOSED / not reachable - Good, e no open to all")
    exit()

# 2. Check HTTP security
try:
    url = f"http://{target}:{port}"
    r = requests.get(url, timeout=5)
    if r.status_code == 200 and "AXIS" in r.text or "Video" in r.text:
        print(f"[+] Camera web page dey show without password!")
        print("[!] RISK: Anybody for your network fit see am")
        print("\n--- HOW TO FIX (PRO Advice) ---")
        print("1. Go to camera settings > Users > Set strong password")
        print("2. Disable anonymous viewing / Guest")
        print("3. Turn off UPnP / Port Forwarding for that camera for router")
        print("4. Update firmware from Axis official site")
    else:
        print(f"[+] Camera dey ask for password - GOOD! Status: {r.status_code}")
except Exception as e:
    print(f"Could not fetch web page: {e}")

print("\n[+] Scan done. This is for YOUR OWN device protection only.")
print("Piuscyber-Hackers - Ethical Hacking = Secure, Not Spy")-