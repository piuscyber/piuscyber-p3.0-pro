import socket
from datetime import datetime

print("--- Piuscyber p3.0 PRO MAX ULTRA ---")

try:
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    print("Computer:", hostname)
    print("Your Local IP:", local_ip)
except:
    local_ip = "127.0.0.1"

PORTS = [80,81,82,84,88,8000,8080,8081,8888,554,8554,1935,37777,34567,5000,7000,9000]

target = input("Enter IP to scan [Press Enter for auto]: ").strip()
if target == "":
    target = local_ip

print("Scanning", target)
print("-" * 40)

open_ports = []
log = []
log.append("Report - " + str(datetime.now()))
log.append("Target: " + target)

for port in PORTS:
    s = socket.socket()
    s.settimeout(1)
    result = s.connect_ex((target, port))
    if result == 0:
        print("Port", port, "OPEN")
        log.append("Port " + str(port) + " OPEN")
        open_ports.append(port)
    else:
        print("Port", port, "CLOSED")
        log.append("Port " + str(port) + " CLOSED")
    s.close()

print("-" * 40)
print("Open:", len(open_ports))
log.append("Open count: " + str(len(open_ports)))

if len(open_ports) == 0:
    log.append("Verdict: Secure! No cam port open")
else:
    log.append("Verdict: Check ports " + str(open_ports))

with open("report.txt", "w") as f:
    for line in log:
        f.write(line + "\n")

print("Done! report.txt saved")