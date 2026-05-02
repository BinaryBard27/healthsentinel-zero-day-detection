# HealthSentinel AI Integration - Startup Guide

## 🚀 Quick Start

Your HealthSentinel website now has **ALL FOUR** trained AI models integrated!

### Prerequisites

- Python 3.8+ (for AI backend)
- Node.js 18+ (for TypeScript backend + React frontend)

---

## Step 1: Start the Python AI Backend (Port 8000)

```bash
# Navigate to AI backend
cd C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\ai_backend

# Install dependencies (first time only)
pip install -r requirements.txt

# Start the server
python ai_server.py
```

**Expected Output:**
```
Loading AI models...
✅ Ransomware models loaded (9 models)
✅ Phishing detection system loaded
✅ SQL Injection CodeBERT model loaded (498 MB)
✅ LSTM model + baselines loaded
✅ All models loaded successfully!

Server running on http://localhost:8000
API Documentation: http://localhost:8000/docs
```

**⏱️ First startup takes 1-2 minutes** to load all models (especially CodeBERT 498MB model).

---

## Step 2: Start the TypeScript Backend (Port 5000)

```bash
# Navigate to backend
cd C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\webpage\backend

# Install dependencies (first time only)
npm install

# Start the server
npm run dev
```

**Expected Output:**
```
✅ Server running on: http://localhost:5000
📧 Email Service: LOCAL TEST (Ethereal Email)

📝 Test Credentials:
   Email: admin@test.com
   Password: admin123
```

---

## Step 3: Start the React Frontend (Port 5173)

```bash
# Navigate to frontend
cd C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\webpage\frontend

# Install dependencies (first time only)
npm install

# Start the development server
npm run dev
```

**Expected Output:**
```
  VITE ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

## 🎯 Using the Application

### 1. **Login**
- Open browser to `http://localhost:5173`
- Click "Login" button
- Enter credentials:
  - Email: `admin@test.com`
  - Password: `admin123`
- Enter the OTP from the server terminal output
- You'll be redirected to the Security Dashboard

### 2. **AI Detection Features**

#### **Ransomware Scanner**
- Enter comma-separated file features (10 values)
- Example: `0.5, 0.3, 0.8, 0.1, 0.9, 0.2, 0.7, 0.4, 0.6, 0.3`
- Get ensemble prediction from 9 models

#### **Phishing Analyzer**
- Enter email details (sender, subject, message)
- Get action: BLOCK, QUARANTINE, or ALLOW
- See detection reasons

#### **SQL Injection Tester**
- Enter SQL query (`SELECT * FROM users WHERE id = '1' OR '1'='1'`)
- CodeBERT analyzes with 99.9% accuracy
- Click example queries for quick testing

#### **Insider Threat Monitor**
- Enter user ID (e.g., `john_doe`)
- LSTM analyzes behavioral patterns
- Get anomaly score and risk level

---

## 🧪 Testing the Integration

### Test Python AI Backend Endpoints

```bash
cd C:\Users\SHERWIN\OneDrive\Documents\Desktop\project\HealthSentinel\ai_backend
python test_api.py
```

Expected: All 5 tests pass ✅

### Test Full Stack Integration

1. **Check AI backend health**: http://localhost:8000/api/health
2. **Check via TypeScript proxy**: http://localhost:5000/api/ai/health
3. **Test from frontend**: Login → Navigate to each tab → Run detections

---

## 📊 What's Integrated

| AI Model | Status | Accuracy | Endpoint |
|----------|--------|----------|----------|
| **Ransomware** | ✅ Running | 9-model ensemble | `/api/ai/ransomware` |
| **Phishing** | ✅ Running | Two-tier system | `/api/ai/phishing` |
| **SQL Injection** | ✅ Running | 99.9% (CodeBERT) | `/api/ai/sql-injection` |
| **Insider Threat** | ✅ Running | LSTM Autoencoder | `/api/ai/insider-threat` |

---

## 🔧 Troubleshooting

### Python Backend won't start
- **Issue**: Module not found
- **Fix**: `pip install -r requirements.txt`

### TypeScript Backend errors
- **Issue**: axios not found
- **Fix**: `cd webpage/backend && npm install`

### Frontend React errors  
- **Issue**: Component type errors
- **Fix**: `cd webpage/frontend && npm install`

### Models loading slow
- **Normal**: First load takes 1-2 minutes (CodeBERT is 498MB)
- **Subsequent starts**: Much faster after first load

### Port already in use
- **Python (8000)**: Change port in `ai_server.py` line 455
- **TypeScript (5000)**: Change in `backend/src/server.ts` line 301
- **React (5173)**: Vite will auto-increment to 5174

---

## 🎉 Success Indicators

✅ Python backend shows "All models loaded successfully!"  
✅ TypeScript backend connects to Python at startup  
✅ Frontend loads without console errors  
✅ Login works with test credentials  
✅ Security Dashboard displays with 4 tabs  
✅ Each AI detector returns results

---

## 📚 API Documentation

Interactive API docs available at: **http://localhost:8000/docs**

Browse all endpoints, test requests, and see response schemas.

---

## 🔐 Production Deployment Notes

Before deploying to production:

1. **Change credentials** in `backend/src/server.ts`
2. **Add real database** instead of in-memory storage
3. **Configure CORS** origins in `ai_server.py` line 28
4. **Set environment variables** for all secrets
5. **Use production SMTP** instead of Ethereal Email
6. **Add rate limiting** on AI endpoints
7. **Enable HTTPS** on all servers
