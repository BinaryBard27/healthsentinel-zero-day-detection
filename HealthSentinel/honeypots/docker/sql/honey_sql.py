import socket
import os
import requests
import time
from datetime import datetime

AGGREGATOR_URL = os.getenv("AGGREGATOR_URL", "http://host.docker.internal:8080/logs")

def send_alert(src_ip, details):
    log = {
        "logs": [{
            "name": "honeypot_alert",
            "hostIdentifier": "HP-DOCKER-SQL",
            "calendarTime": datetime.now().isoformat(),
            "unixTime": int(time.time()),
            "columns": {
                "honeypot": "SQL_Database",
                "action": "DB_Probe",
                "src_ip": src_ip,
                "details": str(details),
                "severity": "critical"
            }
        }]
    }
    try:
        requests.post(AGGREGATOR_URL, json=log, timeout=2)
    except:
        pass

def run():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 5432))
    s.listen(5)
    print("SQL Honeypot ready...")
    while True:
        c, addr = s.accept()
        send_alert(addr[0], "Connection established")
        c.send(b"E\x00\x00\x00\x1fSFATAL\x00C28P01\x00Mpassword authentication failed\x00")
        c.close()

if __name__ == "__main__":
    run()
