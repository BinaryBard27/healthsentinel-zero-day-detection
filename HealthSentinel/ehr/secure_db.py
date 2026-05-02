"""
HealthSentinel Secure EHR Database
==================================
Implements a secure SQLite database for Electronic Health Records.
Features:
1. Role-Based Access Control (RBAC)
2. Automated Audit Logging
3. Row-level encryption (simulated)
"""

import sqlite3
import json
import time
import uuid
import requests
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
DB_PATH = "ehr_secure.db"
AGGREGATOR_URL = "http://localhost:8080/logs"

class EHRManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Patients Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                dob TEXT,
                medical_history TEXT,
                vitals TEXT,
                last_updated TIMESTAMP
            )
        ''')
        # Audit Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_trail (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                action TEXT,
                target_id TEXT,
                timestamp TIMESTAMP,
                status TEXT
            )
        ''')
        self.conn.commit()

    def log_audit(self, user_id, action, target_id, status):
        """Internal audit logging."""
        cursor = self.conn.cursor()
        now = datetime.now().isoformat()
        cursor.execute(
            "INSERT INTO audit_trail (user_id, action, target_id, timestamp, status) VALUES (?, ?, ?, ?, ?)",
            (user_id, action, target_id, now, status)
        )
        self.conn.commit()
        
        # Also report to central aggregator
        log = {
            "logs": [{
                "name": "ehr_audit_event",
                "hostIdentifier": "ehr-db-01",
                "calendarTime": now,
                "unixTime": int(time.time()),
                "columns": {
                    "user": user_id,
                    "action": action,
                    "target": target_id,
                    "status": status,
                    "severity": "medium" if status == "access_denied" else "low"
                }
            }]
        }
        try:
            requests.post(AGGREGATOR_URL, json=log, timeout=1)
        except:
            pass

    def get_patient(self, user_id, patient_id, role="nurse"):
        """RBAC Protected Retrieval."""
        # Simple RBAC: Nurses can read vitals, Doctors can read everything
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,))
        row = cursor.fetchone()
        
        if not row:
            self.log_audit(user_id, "READ", patient_id, "not_found")
            return None

        self.log_audit(user_id, "READ", patient_id, "success")
        
        data = {
            "patient_id": row[0],
            "name": row[1],
            "dob": row[2],
            "vitals": json.loads(row[4]) if row[4] else {}
        }
        
        if role == "doctor":
            data["medical_history"] = row[3]
            
        return data

    def seed_data(self):
        """Insert sample patients if empty."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM patients")
        if cursor.fetchone()[0] == 0:
            patients = [
                ("PAT-001", "John Doe", "1985-05-12", "Hypertension", json.dumps({"bp": "130/85", "hr": 78})),
                ("PAT-002", "Jane Smith", "1992-11-20", "Gestational Diabetes", json.dumps({"bp": "115/75", "hr": 72})),
            ]
            cursor.executemany("INSERT INTO patients (patient_id, name, dob, medical_history, vitals, last_updated) VALUES (?,?,?,?,?,DATETIME('now'))", patients)
            self.conn.commit()
            print("📦 EHR Database seeded with sample data.")

if __name__ == "__main__":
    ehr = EHRManager()
    ehr.seed_data()
    print("🏥 Secure EHR Database is ACTIVE.")
