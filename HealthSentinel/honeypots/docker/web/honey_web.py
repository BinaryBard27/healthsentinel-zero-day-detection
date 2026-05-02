from flask import Flask, request, jsonify
import requests
import time
from datetime import datetime
import os

app = Flask(__name__)
AGGREGATOR_URL = os.getenv("AGGREGATOR_URL", "http://host.docker.internal:8080/logs")

def send_alert(honeypot, action, src_ip, details):
    log = {
        "logs": [{
            "name": "honeypot_alert",
            "hostIdentifier": f"HP-DOCKER-{honeypot}",
            "calendarTime": datetime.now().isoformat(),
            "unixTime": int(time.time()),
            "columns": {
                "honeypot": honeypot,
                "action": action,
                "src_ip": src_ip,
                "details": str(details),
                "severity": "critical",
                "environment": "docker"
            }
        }]
    }
    try:
        requests.post(AGGREGATOR_URL, json=log, timeout=2)
    except:
        pass

@app.route('/')
def index():
    send_alert("WebPortal", "Access", request.remote_addr, "Landed on login page")
    return "<h1>Hospital EHR v4.2</h1><form action='/login' method='POST'>User: <input name='u'><br>Pass: <input type='password' name='p'><br><input type='submit'></form>"

@app.route('/login', methods=['POST'])
def login():
    send_alert("WebPortal", "Login_Attempt", request.remote_addr, f"Creds: {request.form.get('u')}:{request.form.get('p')}")
    return "Unauthorized", 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
