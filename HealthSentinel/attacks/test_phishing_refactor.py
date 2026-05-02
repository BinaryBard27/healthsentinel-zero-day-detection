import asyncio
import sys
from fastapi import Request
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')
from ai_server import model_manager, detect_phishing, PhishingRequest

model_manager.load_all_models()

async def test_endpoint():
    print("================ PHISHING REFACTOR TESTS ================\n")

    def make_req():
        return Request({
            "type": "http", 
            "client": ("127.0.0.1", 8000), 
            "method": "POST", 
            "url": "http://testserver",
            "path": "/api/ai/phishing"
        })

    # Test 1: Fallback (Assuming rule-based if we artificially set model to None, but model IS loaded. 
    # Let's test the Lookalike Detector via ML loaded.)
    
    # Test 1: Lookalike Domain
    print("TEST 1: Lookalike Domain Detector")
    payload = PhishingRequest(
        sender="admin@healthsentineI.internal", # Capital 'I' instead of 'l'
        subject="Invoice attached",
        message="Please pay the invoice.",
        urls=[]
    )
    res = await detect_phishing(payload, make_req())
    print(f"Action: {res.action}")
    print(f"Risk: {res.risk_level}")
    print(f"Confidence: {res.confidence*100:.1f}%")
    print(f"Reasons: {res.reasons[:2]}")
    print("-" * 50)

    # Test 2: Contextual NLP Refinement
    print("TEST 2: Contextual NLP Refinement ('benefits enrollment')")
    payload2 = PhishingRequest(
        sender="hr@healthsentinel.com",
        subject="Benefits Enrollment 2026",
        message="Please complete your benefits enrollment today.",
        urls=[]
    )
    res2 = await detect_phishing(payload2, make_req())
    print(f"Action: {res2.action}")
    print(f"Risk: {res2.risk_level}")
    print(f"Confidence: {res2.confidence*100:.1f}%")
    print("-" * 50)
    
    # Test 3: Domain Whitelist
    print("TEST 3: Domain Whitelist (Internal Domain)")
    payload3 = PhishingRequest(
        sender="bob@healthsentinel.internal",
        subject="Meeting notes",
        message="Urgent meeting notes attached.",
        urls=["http://tinyurl.com/meeting"]
    )
    res3 = await detect_phishing(payload3, make_req())
    print(f"Action: {res3.action}")
    print(f"Risk: {res3.risk_level}")
    print(f"Confidence: {res3.confidence*100:.1f}%")
    print("-" * 50)

    # Test 4: Fallback Rule-Based (>90% Safe)
    print("TEST 4: Fallback Rule-Based (Safe)")
    # Temporarily remove ML models to test fallback
    model_manager.phishing_system = None
    payload4 = PhishingRequest(
        sender="bob@healthsentinel.internal",
        subject="Lunch",
        message="Are we still going to lunch?",
        urls=[]
    )
    res4 = await detect_phishing(payload4, make_req())
    print(f"Action: {res4.action}")
    print(f"Risk: {res4.risk_level}")
    print(f"Confidence: {res4.confidence*100:.1f}%")
    print("=========================================================\n")

if __name__ == "__main__":
    asyncio.run(test_endpoint())
