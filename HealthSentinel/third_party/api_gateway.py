"""
Third-Party API Gateway & Model Guard (Phase 3)
==============================================
Enforces security on incoming requests from third-party apps.
Uses CodeBERT (simulated for now) to detect SQL injection in API calls.
"""

from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import time
import requests
from datetime import datetime

app = FastAPI(title="HealthSentinel Third-Party API Gateway")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ═══════════════════════════════════════════════════════════════════════════════
AGGREGATOR_URL = "http://localhost:8080/logs"
ZT_CONTROLLER_URL = "http://localhost:8081/authorize"

class PatientRequest(BaseModel):
    app_id: str
    patient_id: str
    query_params: str = ""

# ═══════════════════════════════════════════════════════════════════════════════
# AI SCANNER (SIMULATED CODEBERT)
# ═══════════════════════════════════════════════════════════════════════════════

def is_sqli_attack(query: str) -> bool:
    """
    Simulates CodeBERT model inference for SQL injection.
    In production, this would load the CodeBERT model and run inference.
    """
    sql_patterns = ["' OR '1'='1", "UNION SELECT", "DROP TABLE", "--", ";", "SLEEP("]
    return any(p.lower() in query.upper() for p in sql_patterns)

# ═══════════════════════════════════════════════════════════════════════════════
# GATEWAY ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/v1/ehr/patient")
async def get_patient_data(req: PatientRequest):
    """
    1. Check Zero Trust Authorization
    2. Scan for SQL Injection (AI-driven)
    3. Return Data if safe
    """
    
    # 1. Zero Trust Handshake
    zt_payload = {
        "user_id": req.app_id,
        "target_zone": "ehr",
        "action": "read",
        "device_id": "third-party-gateway"
    }
    
    try:
        zt_resp = requests.post(ZT_CONTROLLER_URL, json=zt_payload)
        zt_data = zt_resp.json()
        if not zt_data.get("allowed"):
            raise HTTPException(status_code=403, detail=f"Zero Trust Access Denied: {zt_data.get('reason')}")
    except requests.exceptions.ConnectionError:
        raise HTTPException(status_code=503, detail="Zero Trust Engine Unreachable")

    # 2. SQL Injection Guard (AI Scan)
    if is_sqli_attack(req.query_params):
        log_security_event(req.app_id, "SQL_INJECTION_ATTEMPT", req.query_params)
        raise HTTPException(status_code=400, detail="Security Alert: Malicious characters detected in query parameters")

    # 3. Success (Mock EHR Data)
    return {
        "status": "success",
        "patient": {
            "id": req.patient_id,
            "name": "John Doe",
            "vitals": {"bp": "120/80", "hr": 72}
        },
        "guarded_by": "HealthSentinel AI-Gateway"
    }

def log_security_event(app_id: str, event_type: str, details: str):
    log = {
        "logs": [{
            "name": "third_party_security_event",
            "hostIdentifier": "tp-gateway-01",
            "calendarTime": datetime.now().isoformat(),
            "unixTime": int(time.time()),
            "columns": {
                "app_id": app_id,
                "event_type": event_type,
                "details": details,
                "severity": "high"
            }
        }]
    }
    try:
        requests.post(AGGREGATOR_URL, json=log)
    except:
        pass

if __name__ == "__main__":
    import uvicorn
    print("🛡️ Third-Party API Gateway starting on port 8082...")
    uvicorn.run(app, host="0.0.0.0", port=8082)
