import asyncio
import sys
from fastapi import Request
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')
from ai_server import model_manager, detect_ransomware, RansomwareRequest

model_manager.load_all_models()

async def test_endpoint():
    payload = RansomwareRequest(
        file_features=[0.1, 0.1, 0.1, 0.9, 0.0, 0.98, 0.1, 0.1, 0.1, 0.2],
        file_name="test_interlock.exe",
        fallback_active=False
    )
    
    mock_req = Request({
        "type": "http", 
        "client": ("127.0.0.1", 8000), 
        "method": "POST", 
        "url": "http://testserver",
        "path": "/api/ai/ransomware"
    })
    
    response = await detect_ransomware(payload, mock_req)
    print("================ TEST RESULT ================")
    print(f"Prediction: {response.prediction.upper()} (expected MALICIOUS or RANSOMWARE)")
    print(f"Risk Level: {response.risk_level.upper()}")
    print(f"Confidence: {response.confidence * 100}%")
    if response.ensemble_votes:
        print("Ensemble votes detail:")
        for k, v in response.ensemble_votes.items():
            print(f" - {k}: {v}")
    print("=============================================")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
