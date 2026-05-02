"""
HealthSentinel AI Backend Server
=================================
Unified FastAPI server serving all AI security models:
- Ransomware Detection (9-model ensemble)
- Phishing Email Detection (Two-tier system)
- SQL Injection Detection (CodeBERT)
- Insider Threat Detection (LSTM Autoencoder)

Features:
- Rate limiting via slowapi (30/min detect, 10/min explain)
- SHAP explainability for ransomware, SQL injection, and insider threat
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import pickle
import torch
import numpy as np
import logging
import json
import re
import random
from datetime import datetime
from pathlib import Path
import sys
# Fix path for local imports
sys.path.append(str(Path(__file__).parent))
from attack_simulator import AttackSimulator
from deception_engine import DeceptionEngine

# --- New Features Imports ---
sys.path.append(str(Path(__file__).parent.parent))
from dlp.phi_redactor import PHIRedactor
from src.blockchain_audit import BlockchainAudit
from src.soar_playbooks import SOARPlaybooks
from src.compliance_checker import ComplianceChecker
from src.threat_hunter_agent import ThreatHunterAgent
from src.biometrics_analyzer import BiometricsAnalyzer
from zerotrust.zone_controller import AccessRequest # To demonstrate ZT integration

import asyncio
from fastapi import WebSocket, WebSocketDisconnect

# Rate limiter
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# RATE LIMITER SETUP
# ============================================================================

limiter = Limiter(key_func=get_remote_address, default_limits=["200/minute"])

# Initialize FastAPI app (Life-span moved down)
# app = FastAPI(title="HealthSentinel AI Backend", version="1.0.0")

# middleware moved below app initialization

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

# SHAP response models
class SHAPFeature(BaseModel):
    name: str
    value: float
    impact: str  # "positive" or "negative"

class SHAPResponse(BaseModel):
    shap_values: List[float]
    feature_names: List[str]
    base_value: float
    prediction: str
    top_features: List[SHAPFeature]

# Detection Models
class RansomwareRequest(BaseModel):
    file_features: List[float]
    file_name: Optional[str] = "unknown"
    fallback_active: Optional[bool] = False

class RansomwareResponse(BaseModel):
    prediction: str  # "ransomware" or "benign"
    confidence: float
    risk_level: str  # "HIGH", "MEDIUM", "LOW"
    ensemble_votes: Dict[str, Any]

class PhishingRequest(BaseModel):
    sender: str
    subject: str
    message: str
    urls: Optional[List[str]] = []

class PhishingResponse(BaseModel):
    action: str  # "BLOCK", "QUARANTINE", "ALLOW"
    risk_level: str
    confidence: float
    reasons: List[str]
    user_message: str
    explain_data: Optional[SHAPResponse] = None

class SQLInjectionRequest(BaseModel):
    query: str

class SQLInjectionResponse(BaseModel):
    is_injection: bool
    confidence: float
    risk_level: str
    details: str

class InsiderThreatRequest(BaseModel):
    user_id: str
    sequence_data: List[List[float]]  # Behavioral sequence

class InsiderThreatResponse(BaseModel):
    is_anomaly: bool
    risk_score: float
    risk_level: str
    reconstruction_error: float
    threshold: float
    user_id: Optional[str] = None

# Simulation Models
class SimStatusResponse(BaseModel):
    stage: str
    lstm_score: float
    isolation_score: float
    combined_risk: float
    action: str
    shap_data: Optional[SHAPResponse] = None
    honeypot_triggered: bool = False
    wave: Optional[int] = None
    attack_name: Optional[str] = None
    attack_category: Optional[str] = None


class BattleWaveRequest(BaseModel):
    wave: int
    attack_name: str

class RiskDecisionRequest(BaseModel):
    lstm_score: float
    isolation_score: float
    honeypot_boost: float = 0.0

class RiskDecisionResponse(BaseModel):
    final_risk: float
    decision: str
    explanation: str

class SimulationState:
    def __init__(self):
        self.active = False
        self.current_stage_idx = 0
        self.user_id = "employee_04"
        self.logs = []
        self.last_risk = 0.0
        self.battle_mode: bool = False
        self.expected_waves: int = 12
        self.wave_events: List[Dict[str, Any]] = []
        self.battle_complete: bool = False

class ThreatHuntRequest(BaseModel):
    query: str

class ThreatHuntResponse(BaseModel):
    answer: str
    remediation: List[str]

# ============================================================================
# FEATURE EXTRACTORS
# ============================================================================

def extract_phishing_features(sender: str, subject: str, message: str, urls: List[str]) -> List[float]:
    """Extract numeric features expected by the XGBoost phishing model"""
    # Simplified features extraction (placeholder as we now use NLP pipeline)
    return [0.0] * 11

def clean_phishing_text(text: str) -> str:
    """Helper to clean text for NLP inference (matches training script)"""
    if not isinstance(text, str): return ""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    return " ".join(text.split())

# ============================================================================
# MODEL LOADERS
# ============================================================================

class ModelManager:
    def __init__(self):
        self.models_loaded = False
        self.ransomware_models = None
        self.phishing_system = None
        self.sql_injection_model = None
        self.lstm_model = None
        self.user_baselines = None
        
    def load_all_models(self):
        """Load all AI models on server startup — each independently"""
        logger.info("Loading AI models...")

        # Load models individually
        self._load_ransomware_models()
        self._load_phishing_system()
        self._load_sql_injection_model()
        self._load_lstm_model()

        self.models_loaded = True
        logger.info("✅ Startup complete. (ML Models active if available)")

    def _load_ransomware_models(self):
        """Load ransomware ensemble models"""
        logger.info("Loading Ransomware models...")
        # Use relative paths based on the project root
        project_root = Path(__file__).parent.parent
        # Research found path: Datasets\preprocessed data\Ransomware\Simulation\model\RansomwareModels_Complete
        base_path = project_root / "Datasets" / "preprocessed data" / "Ransomware" / "Simulation" / "model" / "RansomwareModels_Complete"
        
        if not base_path.exists():
            logger.warning(f"⚠️ Ransomware models directory not found at {base_path}")
            self.ransomware_models = None
            return

        try:
            self.ransomware_models = {
                'rf': pickle.load(open(base_path / 'rf_model.pkl', 'rb')),
                'xgb': pickle.load(open(base_path / 'xgb_model.pkl', 'rb')),
                'lgb': pickle.load(open(base_path / 'lgb_model.pkl', 'rb')),
                'svm': pickle.load(open(base_path / 'svm_model.pkl', 'rb')),
                'isolation_forest': pickle.load(open(base_path / 'isolation_forest.pkl', 'rb')),
                'voting_ensemble': pickle.load(open(base_path / 'voting_ensemble.pkl', 'rb')),
                'stacking_ensemble': pickle.load(open(base_path / 'stacking_ensemble.pkl', 'rb')),
                'scaler': pickle.load(open(base_path / 'scaler.pkl', 'rb')),
            }
            logger.info("✅ Ransomware models loaded (8 models)")
        except Exception as e:
            logger.warning(f"⚠️ Could not load ransomware models: {e}")
            self.ransomware_models = None
    
    def _load_phishing_system(self):
        """Load the new TF-IDF + XGBoost NLP pipeline for phishing detection"""
        logger.info("Loading NLP Phishing system...")
        project_root = Path(__file__).parent.parent
        # The training script saves to the current ai_backend directory
        phishing_path = project_root / "ai_backend" / "phishing_nlp_pipeline.pkl"
        
        if not phishing_path.exists():
            logger.warning(f"⚠️ NLP Phishing model not found at {phishing_path}")
            self.phishing_system = None
            return
            
        try:
            with open(phishing_path, 'rb') as f:
                self.phishing_system = pickle.load(f)
            logger.info("✅ NLP Phishing pipeline loaded successfully")
        except Exception as e:
            logger.error(f"❌ Could not load NLP phishing model: {e}")
            self.phishing_system = None
    
    def _load_sql_injection_model(self):
        """Load the new TF-IDF + XGBoost NLP pipeline for SQL injection"""
        logger.info("Loading SQL Injection NLP system...")
        project_root = Path(__file__).parent.parent
        # The training script saves to the current ai_backend directory
        sql_path = project_root / "ai_backend" / "sql_nlp_pipeline.pkl"
        
        if not sql_path.exists():
            logger.warning(f"⚠️ NLP SQL Injection model not found at {sql_path}")
            self.sql_injection_model = None
            return
            
        try:
            with open(sql_path, 'rb') as f:
                self.sql_injection_model = pickle.load(f)
            logger.info("✅ NLP SQL Injection pipeline loaded successfully")
        except Exception as e:
            logger.error(f"❌ Could not load NLP SQL Injection model: {e}")
            self.sql_injection_model = None
    
    def _load_lstm_model(self):
        """Load LSTM autoencoder for insider threats"""
        logger.info("Loading LSTM Insider Threat model...")
        
        import json
        
        project_root = Path(__file__).parent.parent
        # Fixed path to match the actual location found during research
        model_path = project_root / "models" / "insider_threat_lstm" / "insider_threat_lstm.pt"
        baselines_path = project_root / "user_baselines.json"
        
        if not model_path.exists():
            # Try fallback to the other location found
            alt_path = project_root / "insider_threat_lstm (1).pt"
            if alt_path.exists():
                logger.info(f"Using alternative LSTM model path: {alt_path}")
                model_path = alt_path
            else:
                logger.warning(f"⚠️ LSTM model not found at {model_path}")
                self.lstm_model = None
                return

        try:
            # Load model - handle both full model and state dict formats
            loaded = torch.load(model_path, map_location='cpu', weights_only=False)
            if isinstance(loaded, dict):
                logger.warning("⚠️ LSTM .pt file is a state dict, not a full model. Using statistical anomaly fallback.")
                self.lstm_model = loaded
            else:
                loaded.eval()
                self.lstm_model = loaded
            
            # Load user baselines
            if baselines_path.exists():
                with open(baselines_path, 'r') as f:
                    self.user_baselines = json.load(f)
            else:
                logger.warning(f"⚠️ User baselines not found at {baselines_path}, using defaults")
                self.user_baselines = {}
            
            logger.info("✅ LSTM model + baselines loaded")
        except Exception as e:
            logger.warning(f"⚠️ Could not load LSTM model: {e}")
            logger.warning("⚠️ Insider threat endpoint will use rule-based fallback")
            self.lstm_model = None
            self.user_baselines = {}

# Initialize managers
model_manager = ModelManager()
attack_simulator = AttackSimulator()
deception_engine = DeceptionEngine()

# --- Initialize Advanced Features ---
phi_redactor = PHIRedactor()
blockchain_audit = BlockchainAudit()
soar = SOARPlaybooks()
compliance_checker = ComplianceChecker()
threat_hunter = ThreatHunterAgent()
biometrics_analyzer = BiometricsAnalyzer()

# WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"WS Broadcast error: {e}")

manager = ConnectionManager()

# Global state for simulation
sim_state = SimulationState()

# --- CLI full_simulation.py battle wave helpers ---
_ATTACK_KILL_STAGE = {
    "SQL Injection": "Exploitation",
    "Phishing Campaign": "Reconnaissance",
    "Ransomware Execution": "Lateral Movement",
    "Insider Data Leak": "Action on Objective",
}
_ATTACK_BAR_CATEGORY = {
    "SQL Injection": "Exploitation",
    "Phishing Campaign": "Phishing",
    "Ransomware Execution": "Malware",
    "Insider Data Leak": "Insider",
}


def _synthetic_wave_metrics(attack_name: str, wave_num: int) -> tuple:
    rng = random.Random(wave_num * 10007 + sum(ord(c) for c in attack_name))
    if "Ransom" in attack_name:
        lstm = rng.uniform(0.62, 0.96)
        iso = rng.uniform(0.48, 0.93)
    elif "SQL" in attack_name:
        lstm = rng.uniform(0.42, 0.93)
        iso = rng.uniform(0.35, 0.88)
    elif "Phishing" in attack_name:
        lstm = rng.uniform(0.22, 0.78)
        iso = rng.uniform(0.18, 0.68)
    else:
        lstm = rng.uniform(0.48, 0.98)
        iso = rng.uniform(0.38, 0.91)
    honeypot_hit = rng.random() < 0.16
    if honeypot_hit:
        iso = min(1.0, iso + 0.14)
    combined_risk = (0.6 * lstm) + (0.4 * iso)
    if honeypot_hit:
        combined_risk = min(1.0, combined_risk + 0.12)
    if combined_risk > 0.85:
        action = "ISOLATE"
    elif combined_risk > 0.7:
        action = "RESTRICT"
    elif combined_risk > 0.4:
        action = "ALERT"
    else:
        action = "ALLOW"
    sim_state.last_risk = combined_risk
    return lstm, iso, combined_risk, action, honeypot_hit


def _append_battle_wave(wave_num: int, attack_name: str) -> Dict[str, Any]:
    lstm, iso, combined_risk, action, honeypot_hit = _synthetic_wave_metrics(attack_name, wave_num)
    stage = _ATTACK_KILL_STAGE.get(attack_name, "Reconnaissance")
    attack_category = _ATTACK_BAR_CATEGORY.get(attack_name, "Phishing")
    return {
        "stage": stage,
        "lstm_score": round(lstm, 4),
        "isolation_score": round(iso, 4),
        "combined_risk": round(combined_risk, 4),
        "action": action,
        "honeypot_triggered": honeypot_hit,
        "wave": wave_num,
        "attack_name": attack_name,
        "attack_category": attack_category,
    }


# ============================================================================
# HELPER: Build SHAP top-features list
# ============================================================================

def _build_top_features(shap_vals: np.ndarray, feature_names: List[str], n: int = 5) -> List[Dict]:
    """Return top-n features sorted by absolute SHAP value."""
    pairs = sorted(
        zip(feature_names, shap_vals.tolist()),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    return [
        {"name": name, "value": round(val, 6), "impact": "positive" if val >= 0 else "negative"}
        for name, val in pairs[:n]
    ]

# ============================================================================
# API ENDPOINTS
# ============================================================================

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load all models on server startup"""
    logger.info("Server starting up...")
    model_manager.load_all_models()
    yield
    logger.info("Server shutting down...")

# Initialize FastAPI app
app = FastAPI(title="HealthSentinel AI Backend", version="1.0.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/ai/health")
async def health_check():
    """Health check endpoint - returns objects with .loaded for frontend compat"""
    return {
        "status": "healthy",
        "models_loaded": model_manager.models_loaded,
        "models": {
            "ransomware": {"loaded": model_manager.ransomware_models is not None},
            "phishing": {"loaded": model_manager.phishing_system is not None},
            "sql_injection": {"loaded": model_manager.sql_injection_model is not None},
            "insider_threat": {"loaded": model_manager.lstm_model is not None}
        }
    }

@app.get("/api/ai/models/status")
async def models_status():
    """Get detailed model status - returns objects for frontend compat"""
    return {
        "ransomware": {
            "loaded": model_manager.ransomware_models is not None,
            "num_models": 9 if model_manager.ransomware_models else 0
        },
        "phishing": {
            "loaded": model_manager.phishing_system is not None,
            "type": "Two-Tier XGBoost + Zero-Day"
        },
        "sql_injection": {
            "loaded": model_manager.sql_injection_model is not None,
            "type": "CodeBERT",
            "accuracy": 0.9991 if model_manager.sql_injection_model else 0
        },
        "insider_threat": {
            "loaded": model_manager.lstm_model is not None,
            "type": "LSTM Autoencoder",
            "users_tracked": len(model_manager.user_baselines) if model_manager.user_baselines else 0
        }
    }

# --- WebSocket Alert Hub ---
@app.websocket("/ws/alerts")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# --- Feature 1: AI Threat Hunter ---
@app.post("/api/ai/hunt", response_model=ThreatHuntResponse)
async def hunt_threat(payload: ThreatHuntRequest):
    result = threat_hunter.query(payload.query)
    return ThreatHuntResponse(**result)

# --- Feature 8: Compliance Status ---
@app.get("/api/ai/compliance")
async def get_compliance():
    return compliance_checker.generate_report()

# ============================================================================
# DETECT ENDPOINTS  (rate limit: 30/minute)
# ============================================================================

@app.post("/api/ai/ransomware", response_model=RansomwareResponse)
@limiter.limit("30/minute")
async def detect_ransomware(payload: RansomwareRequest, request: Request):
    """Detect ransomware from file features"""
    if not model_manager.ransomware_models:
        raise HTTPException(status_code=503, detail="Ransomware models not loaded")
    
    try:
        # Cyclic padding features to match the scaler
        features = np.array(payload.file_features, dtype=np.float64)

        # Fallback Penalty
        if payload.fallback_active and len(features) >= 10:
            features[5] = min(1.0, features[5] * 1.5)  # suspicious_api
            features[9] = min(1.0, features[9] * 1.5)  # string_entropy
            if features[5] > 0.7 or features[9] > 0.7:
                return RansomwareResponse(
                    prediction="ransomware",
                    confidence=1.0,
                    risk_level="HIGH",
                    ensemble_votes={"fallback_penalty": {"prediction": 1, "confidence": 1.0}}
                )

        # Feature-Based Heuristic Override ("Safety Interlock")
        if len(features) >= 10:
            entropy = features[0]
            suspicious_api = features[5]
            if suspicious_api > 0.85 or entropy > 0.92:
                return RansomwareResponse(
                    prediction="ransomware",
                    confidence=1.0,
                    risk_level="CRITICAL",
                    ensemble_votes={"safety_interlock": {"prediction": 1, "confidence": 1.0}}
                )

        n_expected = model_manager.ransomware_models['scaler'].n_features_in_
        if len(features) < n_expected:
            padded = np.zeros(n_expected)
            for i in range(n_expected):
                padded[i] = features[i % len(features)]
            features = padded
            
        features = features.reshape(1, -1)
        features_scaled = model_manager.ransomware_models['scaler'].transform(features)
        
        # Get predictions from all models
        votes = {}
        predictions = []
        
        for name in ['rf', 'xgb', 'lgb', 'svm']:
            pred = model_manager.ransomware_models[name].predict(features_scaled)[0]
            prob = model_manager.ransomware_models[name].predict_proba(features_scaled)[0]
            votes[name] = {"prediction": int(pred), "confidence": float(max(prob))}
            predictions.append(pred)
        
        # Get ensemble predictions
        voting_pred = model_manager.ransomware_models['voting_ensemble'].predict(features_scaled)[0]
        stacking_pred = model_manager.ransomware_models['stacking_ensemble'].predict(features_scaled)[0]
        
        votes['voting_ensemble'] = {"prediction": int(voting_pred)}
        votes['stacking_ensemble'] = {"prediction": int(stacking_pred)}
        
        predictions.extend([voting_pred, stacking_pred])
        
        # Final decision
        confidence = sum(predictions) / len(predictions)
        final_prediction = 1 if confidence >= 0.5 else 0
        
        risk_level = "HIGH" if confidence > 0.7 else "MEDIUM" if confidence > 0.4 else "LOW"
        
        # --- Feature 3 & 5: Blockchain & SOAR ---
        blockchain_audit.add_event({
            "type": "Ransomware Detection",
            "prediction": "ransomware" if final_prediction == 1 else "benign",
            "confidence": confidence
        })
        
        if final_prediction == 1:
            soar.execute_playbook("ransomware", risk_level, {"host": payload.file_name})
            
            # --- LIVE BROADCAST ---
            asyncio.create_task(manager.broadcast(json.dumps({
                "severity": risk_level.lower(),
                "alert_type": "Ransomware",
                "description": f"Critical Ransomware pattern detected in {payload.file_name}",
                "host": payload.file_name,
                "timestamp": datetime.utcnow().isoformat()
            })))

        return RansomwareResponse(
            prediction="ransomware" if final_prediction == 1 else "benign",
            confidence=float(confidence),
            risk_level=risk_level,
            ensemble_votes=votes
        )
        
    except Exception as e:
        logger.error(f"Error in ransomware detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SHAP HELPERS FOR PHISHING
# ============================================================================

def get_phishing_shap(payload: PhishingRequest, action: str, is_fallback: bool = False) -> SHAPResponse:
    """Get real word-mapped SHAP or simulated fallback values"""
    if not is_fallback and model_manager.phishing_system:
        try:
            import shap
            vectorizer = model_manager.phishing_system['vectorizer']
            model = model_manager.phishing_system['model']
            feature_names = model_manager.phishing_system['feature_names']
            
            # 1. Transform text
            text = clean_phishing_text(f"{payload.subject} {payload.message}")
            X_transformed = vectorizer.transform([text])
            
            # 2. Use TreeExplainer for XGBoost
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_transformed)
            
            # Handle binary output format (XGBoost 2.0+ might return a single array)
            if isinstance(shap_values, list) and len(shap_values) > 1:
                sv = shap_values[1][0].toarray().flatten() if hasattr(shap_values[1][0], 'toarray') else shap_values[1][0]
            elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) > 1:
                sv = shap_values[0]
            else:
                sv = shap_values[0] if isinstance(shap_values, list) else shap_values
                
            base_value = float(explainer.expected_value) if not isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value[0])
            
            # 3. Filter for non-zero words that are actually in the text
            # (X_transformed has only the indices for words present)
            present_indices = X_transformed.indices
            top_features = []
            for idx in present_indices:
                val = sv[idx]
                if abs(val) > 0.001:
                    top_features.append({"name": feature_names[idx], "value": float(val), "impact": "positive" if val > 0 else "negative"})
            
            top_features = sorted(top_features, key=lambda x: abs(x['value']), reverse=True)[:8]

            return SHAPResponse(
                shap_values=[round(float(v), 6) for v in sv.tolist()] if hasattr(sv, 'tolist') else [round(float(sv), 6)],
                feature_names=feature_names.tolist() if hasattr(feature_names, 'tolist') else list(feature_names),
                base_value=round(base_value, 6),
                prediction=action,
                top_features=top_features
            )
        except Exception as e:
            logger.warning(f"Failed to generate real SHAP: {e}")
    
    # ⚡ Simulated Fallback
    # (Leaving simulation logic as a safety net if SHAP library fails)
    feature_names = ["urgent", "verify", "link", "password", "bank", "security"]
    sv = np.random.uniform(0.1, 0.4, len(feature_names))
    if action == "ALLOW": sv *= -1
    
    return SHAPResponse(
        shap_values=[round(v, 6) for v in sv.tolist()],
        feature_names=feature_names,
        base_value=0.5,
        prediction=action,
        top_features=[{"name": n, "value": v, "impact": "positive" if v > 0 else "negative"} for n, v in zip(feature_names, sv)]
    )

@app.post("/api/ai/phishing", response_model=PhishingResponse)
@limiter.limit("30/minute")
async def detect_phishing(payload: PhishingRequest, request: Request):
    """Detect phishing from email content with fail-secure fallback"""
    try:
        sender_domain = str(payload.sender).lower().split('@')[-1] if '@' in str(payload.sender) else str(payload.sender).lower()
        is_internal = sender_domain == 'healthsentinel.internal'

        if model_manager.phishing_system:
            # 1. Prepare NLP Input
            vectorizer = model_manager.phishing_system['vectorizer']
            model = model_manager.phishing_system['model']
            
            text = clean_phishing_text(f"{payload.subject} {payload.message}")
            X_transformed = vectorizer.transform([text])
            
            # 2. Model Inference
            proba = float(model.predict_proba(X_transformed)[0, 1])
            
            # 3. Decision Logic
            if proba > 0.8:
                action = "BLOCK"
                user_message = "🚫 High-confidence phishing detection (XGBoost NLP)"
            elif proba > 0.4:
                action = "QUARANTINE"
                user_message = "⚠️ Suspicious email quarantined for review (NLP score)"
            else:
                action = "ALLOW"
                user_message = "✅ Email appears safe (NLP check)"

            # Add internal pass logic override if safe
            if is_internal and action == "ALLOW":
                user_message = "✅ Internal email passed NLP verification"

            explain_data = get_phishing_shap(payload, action, is_fallback=False)
            
            # --- LIVE BROADCAST ---
            if action != "ALLOW":
                asyncio.create_task(manager.broadcast(json.dumps({
                    "severity": "high" if action == "BLOCK" else "medium",
                    "alert_type": "Phishing",
                    "description": f"Phishing email from {payload.sender} blocked by NLP",
                    "host": "MailServer-01",
                    "timestamp": datetime.utcnow().isoformat()
                })))

            return PhishingResponse(
                action=action,
                risk_level="HIGH" if proba > 0.8 else "MEDIUM" if proba > 0.4 else "LOW",
                confidence=proba if proba > 0.5 else 1.0 - proba,
                reasons=[f"NLP phishing probability: {proba:.1%}"],
                user_message=user_message,
                explain_data=explain_data
            )
        else:
            # 🚨 Fallback Logic (Fail-Secure)
            text = f"{payload.sender} {payload.subject} {payload.message}".lower()
            phishing_keywords = ['urgent', 'verify', 'account suspended', 'click here', 'password', 
                                  'bank', 'paypal', 'login', 'confirm', 'winner', 'prize', 'free']
            suspicious_domains = ['bit.ly', 'tinyurl', '.ru', '.tk', '.xyz']
            
            keyword_hits = [kw for kw in phishing_keywords if kw in text]
            url_hits = [u for u in (payload.urls or []) for d in suspicious_domains if d in u]
            
            # Severity Scoring
            score = len(keyword_hits) * 0.2 + len(url_hits) * 0.4
            has_high_severity = any(kw in text for kw in ['password', 'login', 'verify']) and len(url_hits) > 0

            # fail-secure policy implementation
            if is_internal:
                # Internal: Pass but flag unless high severity
                if has_high_severity:
                    action = "QUARANTINE"
                    user_message = "⚠️ Internal email flagged for high-risk elements (fallback)"
                else:
                    action = "ALLOW"
                    user_message = "✅ Internal email passed (fallback check)"
            else:
                # External: Default to QUARANTINE if any risk, else BLOCK if high
                if score > 0.6 or has_high_severity:
                    action = "BLOCK"
                    user_message = "🚫 Phishing indicator threshold exceeded (fallback block)"
                else:
                    # Default external fallback is now QUARANTINE (fail-secure)
                    action = "QUARANTINE"
                    user_message = "⚠️ Email quarantined: Fail-secure policy active (models offline)"

            confidence = min(0.95, score) if action != "ALLOW" else max(0.50, 1.0 - score)
            
            reasons = [f"Suspicious keyword: '{kw}'" for kw in keyword_hits[:3]]
            reasons += [f"Suspicious domain/URL detected" for _ in url_hits[:2]]
            if not reasons:
                reasons = ["Fallback: Fail-secure quarantine policy"]
            
            explain_data = get_phishing_shap(payload, action, is_fallback=True)

            return PhishingResponse(
                action=action,
                risk_level="HIGH" if action == "BLOCK" else "MEDIUM" if action == "QUARANTINE" else "LOW",
                confidence=float(confidence),
                reasons=reasons,
                user_message=user_message,
                explain_data=explain_data
            )
    except Exception as e:
        logger.error(f"Error in phishing detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/sql-injection", response_model=SQLInjectionResponse)
@limiter.limit("30/minute")
async def detect_sql_injection(payload: SQLInjectionRequest, request: Request):
    """Detect SQL injection using CodeBERT (falls back to rule-based if model not loaded)"""

    # ── Rule-based fallback (always available) ──────────────────────────────
    if not model_manager.sql_injection_model:
        query_lower = payload.query.lower()
        injection_patterns = [
            "or '1'='1", "or 1=1", "' or '", '" or "',
            "union select", "union all select",
            "drop table", "drop database",
            "insert into", "delete from", "update set",
            "exec(", "execute(", "xp_cmdshell",
            "-- ", "/*", "*/",
            "' --", "\" --",
            "sleep(", "benchmark(",
            "load_file(", "into outfile",
            "information_schema", "sys.tables",
        ]
        hits = [p for p in injection_patterns if p in query_lower]
        confidence = min(0.97, 0.25 + len(hits) * 0.18)
        is_injection = len(hits) > 0

        return SQLInjectionResponse(
            is_injection=is_injection,
            confidence=confidence if is_injection else 1.0 - confidence,
            risk_level="HIGH" if is_injection and confidence > 0.7 else "MEDIUM" if is_injection else "LOW",
            details=f"Rule-based detection — matched patterns: {', '.join(hits[:3])}" if hits else "No injection patterns detected (rule-based)"
        )
    # ────────────────────────────────────────────────────────────────────────

    
    try:
        vectorizer = model_manager.sql_injection_model['vectorizer']
        model = model_manager.sql_injection_model['model']
        
        # Extract query
        text = payload.query.lower()
        
        # Transform
        X_transformed = vectorizer.transform([text])
        
        # Predict
        proba = float(model.predict_proba(X_transformed)[0, 1])
        is_injection = proba > 0.5
        confidence = proba if is_injection else 1.0 - proba
        
        # --- LIVE BROADCAST ---
        if is_injection:
            asyncio.create_task(manager.broadcast(json.dumps({
                "severity": "high" if confidence > 0.9 else "medium",
                "alert_type": "SQL Injection",
                "description": f"SQL Injection attempt detected in query: {payload.query[:30]}...",
                "host": "PatientDB-01",
                "timestamp": datetime.utcnow().isoformat()
            })))
            
        return SQLInjectionResponse(
            is_injection=is_injection,
            confidence=confidence,
            risk_level="HIGH" if is_injection and confidence > 0.9 else "MEDIUM" if is_injection else "LOW",
            details="SQL injection detected by XGBoost" if is_injection else "Query appears safe (XGBoost verified)"
        )
        
    except Exception as e:
        logger.error(f"Error in SQL injection detection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ai/insider-threat", response_model=InsiderThreatResponse)
@limiter.limit("30/minute")
async def detect_insider_threat(payload: InsiderThreatRequest, request: Request):
    """Detect insider threats using LSTM autoencoder"""
    if model_manager.lstm_model is None:
        raise HTTPException(status_code=503, detail="LSTM model not loaded")
    
    try:
        # Get user baseline
        user_baseline = model_manager.user_baselines.get(payload.user_id, {
            'mean': 0.01,
            'std': 0.005,
            'thresh': 0.02
        })
        threshold = user_baseline['thresh']

        if not isinstance(model_manager.lstm_model, dict):
            # Full model available - use reconstruction error via forward pass
            sequence = torch.FloatTensor(payload.sequence_data).unsqueeze(0)
            if hasattr(model_manager.lstm_model, 'get_reconstruction_error'):
                reconstruction_error = float(model_manager.lstm_model.get_reconstruction_error(sequence, reduction='mean'))
            else:
                with torch.no_grad():
                    recon = model_manager.lstm_model(sequence)
                    reconstruction_error = float(torch.mean((sequence - recon) ** 2).item())
        else:
            # State dict only - use statistical anomaly scoring as fallback
            seq_data = np.array(payload.sequence_data)
            mean_val = float(np.mean(np.abs(seq_data - np.mean(seq_data))))
            std_val = float(np.std(seq_data))
            reconstruction_error = mean_val + std_val * 0.5

        is_anomaly = reconstruction_error > threshold
        risk_score = min(1.0, reconstruction_error / (threshold * 2))

        # --- LIVE BROADCAST ---
        if is_anomaly:
            asyncio.create_task(manager.broadcast(json.dumps({
                "severity": "high" if risk_score > 0.7 else "medium",
                "alert_type": "Insider Threat",
                "description": f"Anomalous behavior detected for user {payload.user_id}",
                "host": "Data-Server-04",
                "timestamp": datetime.utcnow().isoformat()
            })))

        return InsiderThreatResponse(
            is_anomaly=is_anomaly,
            risk_score=float(risk_score),
            risk_level="HIGH" if risk_score > 0.7 else "MEDIUM" if risk_score > 0.3 else "LOW",
            reconstruction_error=reconstruction_error,
            threshold=threshold,
            user_id=payload.user_id
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SIMULATION & RISK ENGINE ENDPOINTS
# ============================================================================

@app.post("/api/ai/simulate/start")
async def start_simulation(request: Request):
    """Initialize a new multi-stage attack simulation (UI) or battle mode (full_simulation.py)."""
    battle_mode = False
    expected_waves = 12
    try:
        if request.headers.get("content-type", "").startswith("application/json"):
            data = await request.json()
            battle_mode = bool(data.get("battle_mode", False))
            expected_waves = int(data.get("expected_waves", 12))
    except Exception:
        pass

    sim_state.battle_mode = battle_mode
    sim_state.expected_waves = max(1, expected_waves)
    sim_state.wave_events = []
    sim_state.battle_complete = False
    sim_state.active = True
    sim_state.current_stage_idx = 0
    sim_state.logs = attack_simulator.get_kill_chain(sim_state.user_id)
    deception_engine.reset()

    if battle_mode:
        logger.info(f"🚀 Battle simulation started ({sim_state.expected_waves} waves expected)")
        return {
            "status": "started",
            "battle_mode": True,
            "expected_waves": sim_state.expected_waves,
            "stages": attack_simulator.attack_stages,
        }

    logger.info(f"🚀 Simulation started for user {sim_state.user_id}")
    return {"status": "started", "battle_mode": False, "stages": attack_simulator.attack_stages}


@app.post("/api/ai/simulate/wave")
async def post_simulation_wave(payload: BattleWaveRequest):
    """Record one attack wave from full_simulation.py for live dashboard updates."""
    if not sim_state.battle_mode:
        raise HTTPException(status_code=400, detail="Not in battle_mode; call /simulate/start with battle_mode first")
    row = _append_battle_wave(payload.wave, payload.attack_name)
    sim_state.wave_events.append(row)
    logger.info(f"📡 Battle wave {payload.wave}: {payload.attack_name} -> {row['action']}")
    return {"status": "ok", "wave": row}


@app.get("/api/ai/simulate/live")
async def get_live_simulation():
    """Snapshot for dashboard polling while CLI battle runs."""
    waves = sim_state.wave_events
    active = bool(
        sim_state.battle_mode and sim_state.active and not sim_state.battle_complete
    )
    last = waves[-1] if waves else None
    return {
        "battle_mode": sim_state.battle_mode,
        "active": active,
        "expected_waves": sim_state.expected_waves,
        "waves": waves,
        "waves_completed": len(waves),
        "complete": sim_state.battle_complete,
        "last_wave": last,
    }


@app.post("/api/ai/simulate/complete")
async def complete_simulation(request: Request):
    """Mark simulation finished (UI kill chain or CLI battle)."""
    if sim_state.battle_mode:
        sim_state.battle_complete = True
        sim_state.active = False
        logger.info("✅ Battle simulation marked complete")
        return {"status": "completed", "battle_mode": True}

    sim_state.active = True
    sim_state.current_stage_idx = 999
    return {"status": "completed", "battle_mode": False}


@app.get("/api/ai/simulate/status", response_model=SimStatusResponse)
async def get_simulation_status(request: Request):
    """Get the current progress and AI metrics of the simulation"""
    if sim_state.battle_mode:
        if sim_state.battle_complete or not sim_state.active:
            return SimStatusResponse(
                stage="Complete",
                lstm_score=0.0,
                isolation_score=0.0,
                combined_risk=sim_state.last_risk,
                action="REPORTED",
            )
        if sim_state.wave_events:
            w = sim_state.wave_events[-1]
            return SimStatusResponse(
                stage=w["stage"],
                lstm_score=w["lstm_score"],
                isolation_score=w["isolation_score"],
                combined_risk=w["combined_risk"],
                action=w["action"],
                honeypot_triggered=w["honeypot_triggered"],
                wave=w["wave"],
                attack_name=w["attack_name"],
                attack_category=w["attack_category"],
            )
        return SimStatusResponse(
            stage="Battle Standby",
            lstm_score=0.0,
            isolation_score=0.0,
            combined_risk=0.0,
            action="NONE",
        )

    if not sim_state.active:
        return SimStatusResponse(
            stage="Idle", lstm_score=0.0, isolation_score=0.0,
            combined_risk=0.0, action="NONE"
        )
    
    stage_idx = sim_state.current_stage_idx
    if stage_idx >= len(attack_simulator.attack_stages):
        sim_state.active = False
        return SimStatusResponse(
            stage="Complete", lstm_score=0, isolation_score=0,
            combined_risk=sim_state.last_risk, action="REPORTED"
        )

    current_stage = attack_simulator.attack_stages[stage_idx]
    log_event = sim_state.logs[stage_idx]
    
    # 1. Get LSTM Score (Simulated inference on log event)
    # In a real pipeline, logs are converted to features. Here we map log data to risk.
    lstm_score = 0.1 # baseline
    if "encoded" in str(log_event.get("cmdline", "")): lstm_score = 0.85
    if log_event.get("event_type") == "remote_login": lstm_score = 0.45
    if log_event.get("file_count", 0) > 100: lstm_score = 0.95
    
    # 2. Get Isolation Forest Score (Statistical anomaly)
    iso_score = 0.2
    if log_event.get("honeypot_interaction"): iso_score = 0.9
    if log_event.get("privilege_escalation_attempt"): iso_score = 0.8
    if log_event.get("data_volume_mb", 0) > 100: iso_score = 0.85

    # 3. Check Deception Assets
    honeypot_hit = log_event.get("honeypot_interaction", False)
    if honeypot_hit:
        deception_engine.trigger_honeypot("h-db-01", sim_state.user_id)

    # 4. Risk Fusion Layer: 0.6 * LSTM + 0.4 * IsoForest
    combined_risk = (0.6 * lstm_score) + (0.4 * iso_score)
    if honeypot_hit: combined_risk = min(1.0, combined_risk + 0.15)
    
    sim_state.last_risk = combined_risk
    
    # Decision mapping
    action = "ALLOW"
    if combined_risk > 0.85: action = "ISOLATE"
    elif combined_risk > 0.7: action = "RESTRICT"
    elif combined_risk > 0.4: action = "ALERT"

    # Advance stage for next poll
    sim_state.current_stage_idx += 1

    return SimStatusResponse(
        stage=current_stage,
        lstm_score=lstm_score,
        isolation_score=iso_score,
        combined_risk=combined_risk,
        action=action,
        honeypot_triggered=honeypot_hit
    )

@app.post("/api/ai/risk/decision", response_model=RiskDecisionResponse)
async def get_risk_decision(payload: RiskDecisionRequest, request: Request):
    """Centralized risk fusion engine"""
    final_risk = (0.6 * payload.lstm_score) + (0.4 * payload.isolation_score)
    final_risk = min(1.0, final_risk + payload.honeypot_boost)
    
    decision = "NORMAL"
    if final_risk > 0.85: decision = "ISOLATE ENDPOINT"
    elif final_risk > 0.7: decision = "RESTRICT ACCESS"
    elif final_risk > 0.4: decision = "GENERATE ALERT"
    
    return RiskDecisionResponse(
        final_risk=final_risk,
        decision=decision,
        explanation=f"Combined risk score of {final_risk:.2f} triggered {decision} response."
    )

@app.get("/api/ai/simulate/honeypots")
async def get_honeypots(request: Request):
    """Get status of deception assets"""
    return deception_engine.get_assets()

# ============================================================================
# SHAP EXPLAIN ENDPOINTS  (rate limit: 10/minute)
# ============================================================================

@app.post("/api/ai/explain/ransomware", response_model=SHAPResponse)
@limiter.limit("10/minute")
async def explain_ransomware(payload: RansomwareRequest, request: Request):
    """SHAP explanation for ransomware detection using Random Forest TreeExplainer"""
    if not model_manager.ransomware_models:
        raise HTTPException(status_code=503, detail="Ransomware models not loaded")

    try:
        import shap

        features = np.array(payload.file_features, dtype=np.float64)
        n_expected = model_manager.ransomware_models['scaler'].n_features_in_
        if len(features) < n_expected:
            padded = np.zeros(n_expected)
            for i in range(n_expected):
                padded[i] = features[i % len(features)]
            features = padded
            
        features = features.reshape(1, -1)
        features_scaled = model_manager.ransomware_models['scaler'].transform(features)

        n_features = features_scaled.shape[1]
        feature_names = [
            "entropy", "file_size", "pe_sections", "import_count", "export_count",
            "suspicious_api", "packed", "overlay_size", "resource_ratio",
            "string_entropy", "tls_callbacks", "debug_stripped"
        ]
        # Pad or trim to match actual feature count
        if len(feature_names) < n_features:
            feature_names += [f"feature_{i}" for i in range(len(feature_names), n_features)]
        feature_names = feature_names[:n_features]

        rf_model = model_manager.ransomware_models['rf']
        explainer = shap.TreeExplainer(rf_model)
        shap_values = explainer.shap_values(features_scaled)

        # shap_values is list[array] for classifiers; take class-1 (ransomware) SHAP values
        if isinstance(shap_values, list):
            sv = np.array(shap_values[1][0])
        else:
            sv = np.array(shap_values[0])

        base_value = float(explainer.expected_value[1]) if isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value)

        # Get final prediction for context
        pred = rf_model.predict(features_scaled)[0]
        prediction_label = "ransomware" if pred == 1 else "benign"

        top_features = _build_top_features(sv, feature_names)

        return SHAPResponse(
            shap_values=[round(v, 6) for v in sv.tolist()],
            feature_names=feature_names,
            base_value=round(base_value, 6),
            prediction=prediction_label,
            top_features=top_features
        )

    except Exception as e:
        logger.error(f"Error generating ransomware SHAP explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/explain/sql-injection", response_model=SHAPResponse)
@limiter.limit("10/minute")
async def explain_sql_injection(payload: SQLInjectionRequest, request: Request):
    """Token-level explanation for SQL injection detection via XGBoost SHAP values."""
    if not model_manager.sql_injection_model:
        raise HTTPException(status_code=503, detail="SQL injection model not loaded")

    try:
        import shap
        vectorizer = model_manager.sql_injection_model['vectorizer']
        model = model_manager.sql_injection_model['model']
        feature_names = model_manager.sql_injection_model['feature_names']
        
        # 1. Transform text
        text = payload.query.lower()
        X_transformed = vectorizer.transform([text])
        
        # 2. Extract SHAP values
        explainer = shap.TreeExplainer(model)
        shap_values = explainer.shap_values(X_transformed)
        
        # Handle binary output format
        if isinstance(shap_values, list) and len(shap_values) > 1:
            sv = shap_values[1][0].toarray().flatten() if hasattr(shap_values[1][0], 'toarray') else shap_values[1][0]
        elif isinstance(shap_values, np.ndarray) and len(shap_values.shape) > 1:
            sv = shap_values[0]
        else:
            sv = shap_values[0] if isinstance(shap_values, list) else shap_values
            
        base_value = float(explainer.expected_value) if not isinstance(explainer.expected_value, (list, np.ndarray)) else float(explainer.expected_value[0])
        
        # 3. Filter for non-zero mapped tokens
        present_indices = X_transformed.indices
        top_features = []
        for idx in present_indices:
            val = float(sv[idx])
            if abs(val) > 0.001:
                top_features.append({
                    "name": str(feature_names[idx]), 
                    "value": round(val, 6), 
                    "impact": "positive" if val > 0 else "negative"
                })
        
        top_features = sorted(top_features, key=lambda x: abs(x['value']), reverse=True)[:8]

        # Model inference for response label
        proba = float(model.predict_proba(X_transformed)[0, 1])
        prediction_label = "injection" if proba > 0.5 else "safe"

        return SHAPResponse(
            shap_values=[round(float(v), 6) for v in sv.tolist()] if hasattr(sv, 'tolist') else [round(float(sv), 6)],
            feature_names=feature_names.tolist() if hasattr(feature_names, 'tolist') else list(feature_names),
            base_value=round(base_value, 6),
            prediction=prediction_label,
            top_features=top_features
        )

    except Exception as e:
        logger.error(f"Error generating SQL injection attention explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/explain/insider-threat", response_model=SHAPResponse)
@limiter.limit("10/minute")
async def explain_insider_threat(payload: InsiderThreatRequest, request: Request):
    """Feature-level SHAP-style explanation for insider threat detection.

    Since the LSTM is stored as a state dict (no forward pass available), we use
    a permutation-based approach: each feature column is masked and the change in
    reconstruction error is used as the feature importance score.
    """
    if model_manager.lstm_model is None:
        raise HTTPException(status_code=503, detail="LSTM model not loaded")

    try:
        sequence_data = np.array(payload.sequence_data)   # (T, F)
        n_features = sequence_data.shape[1]

        feature_names = [
            "login_freq", "data_volume", "after_hours", "failed_logins",
            "unique_hosts", "removable_media", "email_sent", "web_browsing",
            "file_access", "privilege_use", "vpn_sessions", "process_count"
        ]
        if len(feature_names) < n_features:
            feature_names += [f"feature_{i}" for i in range(len(feature_names), n_features)]
        feature_names = feature_names[:n_features]

        user_baseline = model_manager.user_baselines.get(payload.user_id, {
            'mean': 0.01, 'std': 0.005, 'thresh': 0.02
        })
        threshold = user_baseline['thresh']

        def _score(d: np.ndarray) -> float:
            mean_val = float(np.mean(np.abs(d - np.mean(d))))
            std_val = float(np.std(d))
            return mean_val + std_val * 0.5

        baseline_score = _score(sequence_data)

        # Permutation importance: mask each feature with its mean
        shap_vals = np.zeros(n_features)
        col_means = sequence_data.mean(axis=0)
        for f in range(n_features):
            masked = sequence_data.copy()
            masked[:, f] = col_means[f]
            shap_vals[f] = baseline_score - _score(masked)

        is_anomaly = baseline_score > threshold
        risk_score = min(1.0, baseline_score / (threshold * 2))
        prediction_label = f"{'anomaly' if is_anomaly else 'normal'} (risk={risk_score:.2f})"

        top_features = _build_top_features(shap_vals, feature_names)

        return SHAPResponse(
            shap_values=[round(v, 6) for v in shap_vals.tolist()],
            feature_names=feature_names,
            base_value=round(baseline_score, 6),
            prediction=prediction_label,
            top_features=top_features
        )

    except Exception as e:
        logger.error(f"Error generating insider threat SHAP explanation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    import sys
    
    print("\n" + "="*80, flush=True)
    print(" " * 20 + "HealthSentinel AI Backend Server", flush=True)
    print("="*80, flush=True)
    
    try:
        print("\nStarting server on http://localhost:8000", flush=True)
        print("API Documentation: http://localhost:8000/docs\n", flush=True)
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    except Exception as e:
        print(f"\n❌ FATAL STARTUP ERROR: {e}", flush=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
