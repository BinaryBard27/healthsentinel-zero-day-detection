"""
HealthSentinel PII/PHI Masking Utility (Day 14)
==============================================
Provides HIPAA-compliant data masking for patient records.
Used to redact sensitive info before it leaves the secure zone.
"""

import re

class DataMasker:
    @staticmethod
    def mask_name(name: str) -> str:
        """John Doe -> J*** D**"""
        if not name: return ""
        parts = name.split()
        masked = [p[0] + "*" * (len(p)-1) for p in parts]
        return " ".join(masked)

    @staticmethod
    def mask_dob(dob: str) -> str:
        """1985-05-12 -> 1985-**-** (Keep year for stats, mask month/day)"""
        if not dob or len(dob) < 4: return "****"
        return f"{dob[:4]}-**-**"

    @staticmethod
    def mask_history(history: str) -> str:
        """Generic redaction for long medical text."""
        return "[REDACTED PHI]"

    @staticmethod
    def mask_record(record: dict, role: str) -> dict:
        """
        Applies masking based on user role.
        Nurses/Doctors get more info, Analytics gets masked info.
        """
        masked = record.copy()
        
        if role == "analytics":
            masked["name"] = DataMasker.mask_name(record.get("name", ""))
            masked["dob"] = DataMasker.mask_dob(record.get("dob", ""))
            if "medical_history" in masked:
                masked["medical_history"] = DataMasker.mask_history(record["medical_history"])
        
        return masked

if __name__ == "__main__":
    test_rec = {
        "name": "Sherwin Williams",
        "dob": "1995-10-15",
        "medical_history": "Recovering from broken arm, allergic to peanuts."
    }
    
    print("Original Record:", test_rec)
    print("Analytics View: ", DataMasker.mask_record(test_rec, "analytics"))
