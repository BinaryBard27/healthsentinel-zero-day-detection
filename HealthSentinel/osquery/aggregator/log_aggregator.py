"""
FastAPI Log Aggregator for OSQuery Events
=========================================
Receives logs from OSQuery agents, stores them, and exposes API for ML training.

Endpoints:
- POST /logs          - Receive logs from OSQuery
- GET  /logs          - Retrieve stored logs
- GET  /logs/export   - Export logs in ML-ready format
- GET  /stats         - Get telemetry statistics
- WS   /ws/alerts     - Real-time alert stream
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import json
import asyncio
import uuid
import torch
import torch.nn as nn
import numpy as np
import os
import requests

# ═══════════════════════════════════════════════════════════════════════════════
# ML MODEL SETUP
# ═══════════════════════════════════════════════════════════════════════════════

MODEL_PATH = r"C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\models\insider_threat_lstm\insider_threat_lstm.pt"
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class Attention(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.attn = nn.Sequential(nn.Linear(dim, dim//2), nn.Tanh(), nn.Linear(dim//2, 1))
    def forward(self, x):
        w = torch.softmax(self.attn(x), dim=1)
        return torch.sum(x * w, dim=1), w

class InsiderThreatLSTM(nn.Module):
    def __init__(self, input_dim=64, hidden=128):
        super().__init__()
        self.proj = nn.Linear(input_dim, hidden)
        self.lstm = nn.LSTM(hidden, hidden, num_layers=2, batch_first=True, bidirectional=True, dropout=0.3)
        self.attn = Attention(hidden * 2)
        self.fc = nn.Sequential(nn.Linear(hidden*2, 128), nn.ReLU(), nn.Dropout(0.3),
                                nn.Linear(128, 64), nn.ReLU(), nn.Dropout(0.2),
                                nn.Linear(64, 1), nn.Sigmoid())
    def forward(self, x):
        x = self.proj(x)
        x, _ = self.lstm(x)
        x, w = self.attn(x)
        return self.fc(x).squeeze(-1), w

# Global model instance
lstm_model = None

def load_ml_model():
    global lstm_model
    if os.path.exists(MODEL_PATH):
        try:
            lstm_model = InsiderThreatLSTM()
            checkpoint = torch.load(MODEL_PATH, map_location=device)
            # Handle both full save and state_dict only
            state_dict = checkpoint.get('model_state_dict', checkpoint)
            lstm_model.load_state_dict(state_dict)
            lstm_model.to(device)
            lstm_model.eval()
            print(f"✅ LSTM Model loaded successfully from {MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading LSTM model: {e}")
            lstm_model = None
    else:
        print(f"⚠️ Model file not found at {MODEL_PATH}. Using heuristic scoring.")

# Event Encoding Logic (must match Colab)
EVENT_TYPES = {"user_login": 0, "file_access": 1, "network": 2, "usb": 3, "process": 4, 
               "off_hours": 5, "sensitive_access": 6, "external_net": 7, "large_file": 8, "high_priv": 9}
SENSITIVE_PATHS = ["/data/patients", "/data/billing", "/data/phi"]
WEBHOOK_URL = os.getenv("ALERT_WEBHOOK_URL") # Optional: Set in environment

def encode_event(event_name, columns):
    features = np.zeros(64, dtype=np.float32)
    ename = event_name.replace("_events", "").replace("user_", "").replace("connections", "").replace("_devices", "").replace("access", "").strip("_")
    
    # Map to short names used in training
    mapping = {
        "login": "user_login", "file": "file_access", "network": "network", 
        "usb": "usb", "process": "process", "off_hours_activity": "off_hours",
        "sensitive_access": "sensitive_access", "external_net": "external_net"
    }
    short_name = mapping.get(ename, ename)
    
    if short_name in EVENT_TYPES:
        features[EVENT_TYPES[short_name]] = 1.0
    
    timestamp = columns.get("time", 0)
    if timestamp:
        hour = datetime.fromtimestamp(timestamp).hour
        features[10] = hour / 24.0
        features[11] = 1.0 if (hour < 7 or hour > 19) else 0.0
    
    size = int(columns.get("size", 0) or 0)
    features[14] = min(size / 1e9, 1.0)
    features[15] = 1.0 if size > 10_000_000 else 0.0
    
    path = str(columns.get("target_path", "")).lower()
    features[18] = 1.0 if any(p in path for p in ["patient", "billing", "phi"]) else 0.0
    
    remote = columns.get("remote_address", "")
    if remote and not remote.startswith(("192.168.", "10.", "127.")):
        features[22] = 1.0
    
    features[26] = 1.0 if columns.get("removable") == "1" else 0.0
    return features

app = FastAPI(
    title="HealthSentinel Log Aggregator",
    description="Central log collection for insider threat detection",
    version="1.0.0"
)

# CORS for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with database in production)
log_store: List[Dict[str, Any]] = []
alert_store: List[Dict[str, Any]] = []
user_activity: Dict[str, List[Dict]] = defaultdict(list)

# WebSocket connections for real-time alerts
active_connections: List[WebSocket] = []


# ═══════════════════════════════════════════════════════════════════════════════
# MODELS
# ═══════════════════════════════════════════════════════════════════════════════

class OSQueryLog(BaseModel):
    name: str  # Query name
    hostIdentifier: str
    calendarTime: str
    unixTime: int
    epoch: int
    counter: int
    columns: Dict[str, Any]
    action: Optional[str] = "added"

class LogBatch(BaseModel):
    logs: List[OSQueryLog]
    node_key: Optional[str] = None

class Alert(BaseModel):
    alert_id: str
    alert_type: str
    severity: str  # low, medium, high, critical
    user_id: Optional[str]
    host: str
    description: str
    timestamp: str
    raw_event: Dict[str, Any]


# ═══════════════════════════════════════════════════════════════════════════════
# RISK SCORING
# ═══════════════════════════════════════════════════════════════════════════════

def calculate_event_risk_ml(user_id: str) -> float:
    """
    Calculate risk score using the trained LSTM model.
    """
    global lstm_model
    if lstm_model is None:
        return 0.0
    
    events = user_activity.get(user_id, [])
    if len(events) < 5: # Not enough history
        return 0.1
        
    # Get last 60 events
    history = events[-60:]
    encoded = [encode_event(e['event'], e['columns']) for e in history]
    
    # Pad if necessary
    if len(encoded) < 60:
        padding = [np.zeros(64, dtype=np.float32) for _ in range(60 - len(encoded))]
        encoded.extend(padding)
    
    # Convert to tensor (1, 60, 64)
    x = torch.FloatTensor(np.array(encoded, dtype=np.float32)).unsqueeze(0).to(device)
    
    with torch.no_grad():
        score, _ = lstm_model(x)
    
    return float(score.item())


def calculate_event_risk(log: OSQueryLog) -> float:
    """
    Calculate risk score. Tries ML first, falls back to heuristic.
    """
    user = log.columns.get('username') or log.columns.get('uid') or 'unknown'
    
    # If ML model is available, use it based on user history
    if lstm_model:
        return calculate_event_risk_ml(user)
        
    # Heuristic fallback (original logic)
    score = 0.0
    cols = log.columns
    # ... rest of heuristic logic stays same or simplified
    hour = datetime.fromtimestamp(log.unixTime).hour
    if hour < 7 or hour > 19: score += 0.3
    username = cols.get('username', '') or cols.get('uid', '')
    if username in ['Administrator', 'root', 'admin', 'SYSTEM']: score += 0.2
    path = cols.get('target_path', '') or cols.get('path', '')
    if any(kw in path.lower() for kw in ['patient', 'medical', 'health', 'billing']): score += 0.25
    remote_addr = cols.get('remote_address', '')
    if remote_addr and not remote_addr.startswith(('192.168.', '10.', '172.16.', '127.')): score += 0.3
    return min(score, 1.0)


def generate_alert(log: OSQueryLog, risk_score: float) -> Optional[Alert]:
    """Generate alert if risk score exceeds threshold."""
    if risk_score < 0.5:
        return None
    
    severity = "low"
    if risk_score >= 0.8:
        severity = "critical"
    elif risk_score >= 0.7:
        severity = "high"
    elif risk_score >= 0.6:
        severity = "medium"
    
    return Alert(
        alert_id=str(uuid.uuid4()),
        alert_type="INSIDER_THREAT",
        severity=severity,
        user_id=log.columns.get('username') or log.columns.get('uid'),
        host=log.hostIdentifier,
        description=f"Suspicious activity detected: {log.name} (risk: {risk_score:.2f})",
        timestamp=datetime.now().isoformat(),
        raw_event={"name": log.name, "columns": log.columns}
    )


# ═══════════════════════════════════════════════════════════════════════════════
# ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/logs")
async def receive_logs(batch: LogBatch):
    """Receive log batch from OSQuery agent."""
    alerts_generated = []
    
    for log in batch.logs:
        # Store raw log
        log_dict = log.dict()
        log_dict['received_at'] = datetime.now().isoformat()
        log_store.append(log_dict)
        
        # Track user activity
        user = log.columns.get('username') or log.columns.get('uid') or 'unknown'
        user_activity[user].append({
            'event': log.name,
            'time': log.unixTime,
            'columns': log.columns
        })
        
        # Calculate risk and generate alert
        risk_score = calculate_event_risk(log)
        alert = generate_alert(log, risk_score)
        if alert:
            alert_store.append(alert.dict())
            alerts_generated.append(alert.dict())
            # Broadcast to WebSocket clients
            await broadcast_alert(alert.dict())
    
    return {
        "status": "success",
        "logs_received": len(batch.logs),
        "alerts_generated": len(alerts_generated)
    }


@app.get("/logs")
async def get_logs(
    limit: int = 100,
    user: Optional[str] = None,
    event_type: Optional[str] = None,
    since: Optional[int] = None  # Unix timestamp
):
    """Retrieve stored logs with optional filtering."""
    filtered = log_store
    
    if user:
        filtered = [l for l in filtered if 
                   l['columns'].get('username') == user or 
                   l['columns'].get('uid') == user]
    
    if event_type:
        filtered = [l for l in filtered if l['name'] == event_type]
    
    if since:
        filtered = [l for l in filtered if l['unixTime'] > since]
    
    return filtered[-limit:]


@app.get("/logs/export")
async def export_logs_for_training(
    window_hours: int = 1,
    format: str = "sequences"  # "sequences" or "flat"
):
    """
    Export logs in ML-ready format.
    Groups events by user into time windows for LSTM training.
    """
    if format == "flat":
        return log_store
    
    # Group by user and 1-hour windows
    sequences = []
    for user, events in user_activity.items():
        if len(events) < 5:  # Skip users with few events
            continue
        
        # Sort by time
        sorted_events = sorted(events, key=lambda x: x['time'])
        
        # Create windows
        window_size = window_hours * 3600  # seconds
        current_window = []
        window_start = sorted_events[0]['time'] if sorted_events else 0
        
        for event in sorted_events:
            if event['time'] - window_start <= window_size:
                current_window.append(event)
            else:
                if current_window:
                    sequences.append({
                        'user': user,
                        'window_start': window_start,
                        'events': current_window
                    })
                current_window = [event]
                window_start = event['time']
        
        if current_window:
            sequences.append({
                'user': user,
                'window_start': window_start,
                'events': current_window
            })
    
    return {
        "total_sequences": len(sequences),
        "sequences": sequences
    }


@app.get("/alerts")
async def get_alerts(limit: int = 50, severity: Optional[str] = None):
    """Retrieve generated alerts."""
    filtered = alert_store
    if severity:
        filtered = [a for a in filtered if a['severity'] == severity]
    return filtered[-limit:]


@app.get("/stats")
async def get_statistics():
    """Get telemetry statistics for dashboard."""
    now = datetime.now()
    last_hour = int((now - timedelta(hours=1)).timestamp())
    
    recent_logs = [l for l in log_store if l.get('unixTime', 0) > last_hour]
    
    event_counts = defaultdict(int)
    for log in recent_logs:
        event_counts[log['name']] += 1
    
    return {
        "total_logs": len(log_store),
        "total_alerts": len(alert_store),
        "logs_last_hour": len(recent_logs),
        "active_users": len(user_activity),
        "event_breakdown": dict(event_counts),
        "critical_alerts": len([a for a in alert_store if a['severity'] == 'critical'])
    }


@app.get("/user/{user_id}/risk")
async def get_user_risk(user_id: str):
    """Get risk assessment for a specific user."""
    user_events = user_activity.get(user_id, [])
    
    if not user_events:
        return {"user": user_id, "risk_score": 0.0, "events": 0}
    
    # Calculate aggregate risk from recent events
    recent_events = user_events[-50:]  # Last 50 events
    total_risk = 0.0
    
    for event in recent_events:
        # Simplified risk calculation
        if event.get('event') in ['large_file_operations', 'external_network_connections']:
            total_risk += 0.3
        if event.get('event') == 'off_hours_activity':
            total_risk += 0.4
        if event.get('event') == 'mass_file_access':
            total_risk += 0.5
    
    avg_risk = min(total_risk / len(recent_events), 1.0) if recent_events else 0.0
    
    return {
        "user": user_id,
        "risk_score": round(avg_risk, 3),
        "total_events": len(user_events),
        "recent_events": len(recent_events)
    }


# ═══════════════════════════════════════════════════════════════════════════════
# WEBSOCKET FOR REAL-TIME ALERTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.websocket("/ws/alerts")
async def websocket_alerts(websocket: WebSocket):
    """WebSocket endpoint for real-time alert streaming to dashboard."""
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            # Keep connection alive
            await websocket.receive_text()
    except WebSocketDisconnect:
        active_connections.remove(websocket)


async def broadcast_alert(alert: Dict):
    """Broadcast alert to all connected WebSocket clients and external webhooks."""
    # 1. WebSocket Broadcast
    for connection in active_connections:
        try:
            await connection.send_json(alert)
        except:
            pass
    
    # 2. External Webhook (Day 5 requirements)
    if WEBHOOK_URL:
        try:
            msg = f"🚨 [{alert['severity'].upper()}] {alert['description']}\nHost: {alert['host']}\nTime: {alert['timestamp']}"
            requests.post(WEBHOOK_URL, json={"text": msg}, timeout=2)
        except:
            print("⚠️ Webhook alert failed")


# ═══════════════════════════════════════════════════════════════════════════════
# STARTUP
# ═══════════════════════════════════════════════════════════════════════════════

@app.on_event("startup")
async def startup():
    load_ml_model()
    print("🏥 HealthSentinel Log Aggregator started")
    print("📡 Listening for OSQuery logs on http://localhost:8085")
    print("📊 Dashboard WebSocket available at ws://localhost:8085/ws/alerts")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8085)
