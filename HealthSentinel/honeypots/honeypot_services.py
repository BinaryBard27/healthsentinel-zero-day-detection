"""
HealthSentinel Multi-Service Honeypot
====================================
Simulates multiple vulnerable services on different ports to trap intruders.

1. Port 5000: Fake EHR Web Portal & Admin Login
2. Port 5432: Fake PostgreSQL Database (SQLi & Brute Force Trap)
3. Port 21:   Fake FTP File Share (Data Exfiltration Trap)
"""

import socket
import threading
import time
import requests
from datetime import datetime
from flask import Flask, request, jsonify

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
AGGREGATOR_URL = "http://localhost:8080/logs"
LOCAL_IP = "127.0.0.1"

def send_alert(honeypot, action, src_ip, details):
    log = {
        "logs": [{
            "name": "honeypot_alert",
            "hostIdentifier": f"HP-{honeypot}",
            "calendarTime": datetime.now().isoformat(),
            "unixTime": int(time.time()),
            "columns": {
                "honeypot": honeypot,
                "action": action,
                "src_ip": src_ip,
                "details": str(details),
                "severity": "critical"
            }
        }]
    }
    try:
        requests.post(AGGREGATOR_URL, json=log, timeout=2)
        print(f"🔥 [HONEYPOT ALERT] {honeypot}: {action} from {src_ip}")
    except:
        print(f"⚠️ Aggregator down. Local log: {honeypot} tripped by {src_ip}")

# ═══════════════════════════════════════════════════════════════════════════════
# 1. WEB PORTAL HONEYPOT (Flask - Port 5000)
# ═══════════════════════════════════════════════════════════════════════════════
web_app = Flask(__name__)

@web_app.route('/')
def index():
    send_alert("EHR_Web_Portal", "Initial Access", request.remote_addr, "Viewed landing page")
    return """
    <html><head><title>Hospital EHR System v4.2</title></head>
    <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
        <h2>🏥 Central Hospital EHR Management</h2>
        <p>System is in restricted mode. Please login to continue.</p>
        <form action='/login' method='POST'>
            User: <input name='u'><br><br>
            Pass: <input type='password' name='p'><br><br>
            <input type='submit' value='Login'>
        </form>
        <hr><small>Build: 02.2026.01 | Restricted Access Only</small>
    </body></html>
    """

@web_app.route('/login', methods=['POST'])
def login():
    u = request.form.get('u')
    p = request.form.get('p')
    send_alert("EHR_Web_Portal", "Login Attempt", request.remote_addr, f"Creds: {u}:{p}")
    return "<h3>Login Failed. Your IP has been logged for security.</h3>", 401

@web_app.route('/api/v1/patients')
def api_patients():
    send_alert("EHR_API", "Unauthorized API Probe", request.remote_addr, "Attempted to list patient directory")
    return jsonify({"error": "Unauthorized Access", "code": 403}), 403

def run_web_honeypot():
    print("🌐 Web Honeypot running on port 5000...")
    web_app.run(host='0.0.0.0', port=5000, threaded=True)

# ═══════════════════════════════════════════════════════════════════════════════
# 2. SQL DATABASE HONEYPOT (TCP - Port 5432)
# ═══════════════════════════════════════════════════════════════════════════════
def run_sql_honeypot():
    print("🐘 SQL Honeypot (PostgreSQL) running on port 5432...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 5432))
    server.listen(5)
    
    while True:
        client, addr = server.accept()
        src_ip = addr[0]
        send_alert("SQL_Database", "Connection", src_ip, "TCP Connection established to port 5432")
        
        try:
            # Send fake PostgreSQL startup error
            client.send(b"E\x00\x00\x00\x1fSFATAL\x00C28P01\x00Mpassword authentication failed for user \"postgres\"\x00")
            data = client.recv(1024)
            if data:
                send_alert("SQL_Database", "Query/Auth Attempt", src_ip, f"Raw data: {data.hex()}")
        except:
            pass
        finally:
            client.close()

# ═══════════════════════════════════════════════════════════════════════════════
# 3. FTP/FILE SHARE HONEYPOT (TCP - Port 21)
# ═══════════════════════════════════════════════════════════════════════════════
def run_ftp_honeypot():
    print("📁 FTP Honeypot running on port 21...")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 21))
    server.listen(5)
    
    while True:
        client, addr = server.accept()
        src_ip = addr[0]
        send_alert("File_Share", "Connection", src_ip, "FTP Connection initiated")
        
        try:
            client.send(b"220 Service ready for new user.\r\n")
            user_data = client.recv(1024)
            send_alert("File_Share", "User Attempt", src_ip, f"Data: {user_data.decode().strip()}")
            client.send(b"331 Password required.\r\n")
            pass_data = client.recv(1024)
            send_alert("File_Share", "Pass Attempt", src_ip, f"Data: {pass_data.decode().strip()}")
            client.send(b"530 Login incorrect.\r\n")
        except:
            pass
        finally:
            client.close()

# ═══════════════════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    # Start Web in main thread, others in background
    threading.Thread(target=run_sql_honeypot, daemon=True).start()
    threading.Thread(target=run_ftp_honeypot, daemon=True).start()
    
    print("\n🍯 HealthSentinel Honeypots activated! Waiting for intrusions...")
    run_web_honeypot()
