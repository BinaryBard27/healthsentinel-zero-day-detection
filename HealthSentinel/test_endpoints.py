"""
HealthSentinel — Corrected End-to-End API Test
"""
import requests, sys

AI  = "http://localhost:8000"
TS  = "http://localhost:5000"
FE  = "http://localhost:5173"
P   = "✅"; F = "❌"
results = []

def test(label, fn):
    try:
        ok, msg = fn()
        sym = P if ok else F
        results.append((sym, label, msg))
        print(f"  {sym}  {label}")
        print(f"       {msg}")
    except Exception as e:
        results.append((F, label, str(e)))
        print(f"  {F}  {label}")
        print(f"       ERROR: {e}")

print("\n" + "="*65)
print("  HealthSentinel — Full Stack API Test")
print("="*65)

# ── 1. AI Backend health ──────────────────────────────────────────────────────
print("\n[1] AI Backend (port 8000)")

def ai_health():
    r = requests.get(f"{AI}/api/health", timeout=5)
    d = r.json()
    return r.status_code == 200 and d.get("status") == "healthy", \
           f"models_loaded={d.get('models_loaded')} models={d.get('models')}"

def ai_ransomware():
    r = requests.post(f"{AI}/api/detect/ransomware", json={
        "file_features": [0.1]*20,
        "file_name": "test_benign.exe"
    }, timeout=10)
    d = r.json()
    return r.status_code == 200, \
           f"prediction={d.get('prediction')} confidence={d.get('confidence')} risk={d.get('risk_level')}"

def ai_phishing():
    r = requests.post(f"{AI}/api/detect/phishing", json={
        "sender": "hacker@evil.com",
        "subject": "Urgent: Your account is compromised - verify now",
        "message": "Click here immediately http://malicious-site.com/login or lose access",
        "urls": ["http://malicious-site.com/login"]
    }, timeout=10)
    d = r.json()
    return r.status_code == 200, \
           f"action={d.get('action')} risk={d.get('risk_level')} confidence={d.get('confidence')}"

def ai_sql():
    r = requests.post(f"{AI}/api/detect/sql-injection", json={
        "query": "SELECT * FROM users WHERE id=1 OR 1=1 --"
    }, timeout=60)
    d = r.json()
    return r.status_code == 200, \
           f"is_injection={d.get('is_injection')} risk={d.get('risk_level')} confidence={d.get('confidence')}"

def ai_insider():
    seq = [[0.9, 0.95, 0.88, 0.1, 0.2, 0.1, 0.3, 0.4, 1.0, 0.8, 0.9, 0.1]] * 20
    r = requests.post(f"{AI}/api/detect/insider-threat", json={
        "user_id": "nurse_01",
        "sequence_data": seq
    }, timeout=10)
    d = r.json()
    return r.status_code == 200, \
           f"is_anomaly={d.get('is_anomaly')} risk_score={d.get('risk_score')} risk_level={d.get('risk_level')}"

test("Health endpoint /api/health",         ai_health)
test("Ransomware detection (9-model)",       ai_ransomware)
test("Phishing detection (rule-based)",      ai_phishing)
test("SQL Injection (CodeBERT)",             ai_sql)
test("Insider Threat (LSTM fallback)",       ai_insider)

# ── 2. TS Backend ─────────────────────────────────────────────────────────────
print("\n[2] TypeScript Backend (port 5000)")

def ts_login():
    r = requests.post(f"{TS}/api/auth/login", json={
        "email": "admin@test.com",
        "password": "admin123"
    }, timeout=5)
    d = r.json()
    return r.status_code in [200, 201], \
           f"status={r.status_code} message={d.get('message','')[:60]}"

def ts_phishing_proxy():
    r = requests.post(f"{TS}/api/ai/phishing", json={
        "sender": "hacker@evil.com",
        "subject": "Urgent: verify now",
        "message": "Click http://malicious-site.com",
        "urls": ["http://malicious-site.com"]
    }, timeout=15)
    d = r.json()
    return r.status_code == 200, \
           f"action={d.get('action')} risk={d.get('risk_level')}"

def ts_insider_proxy():
    seq = [[0.9, 0.95, 0.88, 0.1, 0.2, 0.1, 0.3, 0.4, 1.0, 0.8, 0.9, 0.1]] * 20
    r = requests.post(f"{TS}/api/ai/insider-threat", json={
        "user_id": "nurse_01",
        "sequence_data": seq
    }, timeout=10)
    d = r.json()
    return r.status_code == 200, \
           f"is_anomaly={d.get('is_anomaly')} risk_level={d.get('risk_level')}"

test("Login (admin@test.com)",               ts_login)
test("AI Proxy → Phishing",                  ts_phishing_proxy)
test("AI Proxy → Insider Threat",            ts_insider_proxy)

# ── 3. Frontend ───────────────────────────────────────────────────────────────
print("\n[3] React Frontend (port 5173)")

def fe_loads():
    r = requests.get(FE, timeout=5)
    return r.status_code == 200, f"status={r.status_code} size={len(r.text)} bytes"

test("Frontend HTML loads", fe_loads)

# ── Summary ───────────────────────────────────────────────────────────────────
print("\n" + "="*65)
passed = sum(1 for s,_,_ in results if s == P)
failed = sum(1 for s,_,_ in results if s == F)
print(f"  RESULT: {passed}/{len(results)} tests passed")
if failed:
    print(f"  FAILED:")
    for s,n,m in results:
        if s == F:
            print(f"    • {n}: {m}")
print("="*65 + "\n")
sys.exit(0 if failed == 0 else 1)
