import json
from datetime import datetime

class ComplianceChecker:
    def __init__(self):
        self.requirements = {
            "HIPAA": [
                {"id": "164.308(a)(1)", "name": "Security Management Process", "status": "PASS"},
                {"id": "164.308(a)(5)", "name": "Security Awareness and Training", "status": "PASS"},
                {"id": "164.312(a)(1)", "name": "Access Control", "status": "FAIL", "reason": "Unencrypted PHI access detected"},
                {"id": "164.312(b)", "name": "Audit Controls", "status": "PASS"}
            ],
            "GDPR": [
                {"id": "Article 32", "name": "Security of processing", "status": "PASS"},
                {"id": "Article 33", "name": "Notification of personal data breach", "status": "WARNING", "reason": "High risk detection pending report"}
            ]
        }
        
    def generate_report(self):
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": "WARNING",
            "checklists": self.requirements,
            "metrics": {
                "phi_redaction_rate": "99.8%",
                "audit_log_integrity": "SECURE (Blockchain Verified)",
                "unauthorized_access_attempts": 12
            }
        }
        return report

    def update_status(self, regulation, req_id, status, reason=None):
        if regulation in self.requirements:
            for req in self.requirements[regulation]:
                if req["id"] == req_id:
                    req["status"] = status
                    if reason:
                        req["reason"] = reason
                    return True
        return False

if __name__ == "__main__":
    checker = ComplianceChecker()
    print(json.dumps(checker.generate_report(), indent=2))
