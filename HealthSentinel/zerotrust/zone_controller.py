"""
Zero Trust Zone Controller
==========================
Acts as the Policy Decision Point (PDP). 
Determines access based on User Identity + Device Health + AI Risk Score.

Zones:
1. Public (Internet)
2. EHR (Electronic Health Records)
3. Admin (Internal Management)
4. Medical Devices (IoMT)
5. Third-Party (Vendors)
6. Management (Core Security)
"""

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
import time
from typing import Dict, List, Optional
from datetime import datetime

app = FastAPI(title="HealthSentinel Zero Trust Engine")

# ═══════════════════════════════════════════════════════════════════════════════
# CONFIG & REPOSITORIES
# ═══════════════════════════════════════════════════════════════════════════════

AGGREGATOR_URL = "http://localhost:8080" # Log Aggregator for risk scores

ZONES = {
    "public": {"security_level": 1, "mfa_required": False, "allowed_risk": 1.0},
    "third_party": {"security_level": 2, "mfa_required": True, "allowed_risk": 0.4},
    "ehr": {"security_level": 3, "mfa_required": True, "allowed_risk": 0.3},
    "medical_devices": {"security_level": 5, "mfa_required": True, "allowed_risk": 0.15}, # Striker risk
    "admin": {"security_level": 5, "mfa_required": True, "allowed_risk": 0.1},
    "management": {"security_level": 6, "mfa_required": True, "allowed_risk": 0.05}
}

AUTHORIZED_DEVICES = {
    "PUMP-001": {"type": "Infusion Pump", "model": "Alaris_v3", "firmware_v": "2.1"},
    "MRI-X1": {"type": "MRI Scanner", "model": "GE_Health_X1", "firmware_v": "4.0"},
    "VENT-99": {"type": "Ventilator", "model": "Servo-i", "firmware_v": "1.8"}
}

# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class AccessRequest(BaseModel):
    user_id: str
    target_zone: str
    action: str  # read, write, connect
    device_id: str
    mfa_verified: bool = False

class AccessDecision(BaseModel):
    allowed: bool
    risk_score: float
    reason: str
    token: Optional[str] = None

# ═══════════════════════════════════════════════════════════════════════════════
# ENGINE CORE
# ═══════════════════════════════════════════════════════════════════════════════

def get_ai_risk_score(user_id: str) -> float:
    """Fetch real-time LSTM risk score from log aggregator."""
    try:
        resp = requests.get(f"{AGGREGATOR_URL}/user/{user_id}/risk", timeout=2)
        if resp.status_code == 200:
            return resp.json().get("risk_score", 0.0)
    except:
        print(f"⚠️ Warning: Could not reach AI Risk Hub for {user_id}. Defaulting to high risk.")
        return 0.8 # Fail-secure: default to high risk if AI engine is down
    return 0.5


@app.post("/authorize", response_model=AccessDecision)
async def authorize_access(req: AccessRequest):
    """
    The Zero Trust Decision Loop
    1. Check if zone exists
    2. Get AI Risk Score (LSTM model output)
    3. Verify zone-specific risk threshold
    4. Check MFA requirements
    """
    
    # 1. Zone Validation
    if req.target_zone not in ZONES:
        return AccessDecision(allowed=False, risk_score=1.0, reason="Invalid Target Zone")

    zone_config = ZONES[req.target_zone]
    
    # 2. Real-time AI Risk Check (The "Brains")
    ai_risk = get_ai_risk_score(req.user_id)
    
    # 3. Decision Logic
    is_allowed = True
    reason = "Access Granted - Risk within limits"
    
    # A. Check Risk Threshold
    if ai_risk > zone_config["allowed_risk"]:
        is_allowed = False
        reason = f"Access Denied - AI Risk Score too high ({ai_risk:.2f} > {zone_config['allowed_risk']})"
    
    # B. Check MFA
    elif zone_config["mfa_required"] and not req.mfa_verified:
        is_allowed = False
        reason = "Access Denied - MFA verification required for this zone"
        
    # C. Device Posture & Device ID Validation
    if req.target_zone == "medical_devices":
        if req.device_id not in AUTHORIZED_DEVICES:
            is_allowed = False
            reason = f"Access Denied - Unauthorized Device ID ({req.device_id})"
        elif ai_risk > 0.1: # Even stricter for medical devices
            is_allowed = False
            reason = f"Access Denied - Extreme sensitive zone (Max Risk 0.1 < current {ai_risk:.2f})"
    
    elif "compromised" in req.device_id.lower():
        is_allowed = False
        reason = "Access Denied - Source device health check failed"

    # 4. Log the decision
    log_decision(req, is_allowed, ai_risk, reason)

    return AccessDecision(
        allowed=is_allowed,
        risk_score=ai_risk,
        reason=reason,
        token=str(uuid.uuid4()) if is_allowed else None
    )


def log_decision(req, allowed, risk, reason):
    """Send access control logs to aggregator for audit trail."""
    log = {
        "logs": [{
            "name": "zero_trust_decision",
            "hostIdentifier": "zt-controller-01",
            "calendarTime": datetime.now().isoformat(),
            "unixTime": int(time.time()),
            "columns": {
                "user": req.user_id,
                "target": req.target_zone,
                "allowed": str(allowed),
                "ai_risk": f"{risk:.2f}",
                "reason": reason
            }
        }]
    }
    try:
        requests.post(f"{AGGREGATOR_URL}/logs", json=log)
    except:
        pass

import uuid

if __name__ == "__main__":
    import uvicorn
    print(f"🛡️ Zero Trust Zone Controller starting...")
    print(f"Micro-segmentation active for {len(ZONES)} zones.")
    uvicorn.run(app, host="0.0.0.0", port=8081)
