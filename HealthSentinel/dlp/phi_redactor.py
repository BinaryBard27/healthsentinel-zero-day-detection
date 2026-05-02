import re
from typing import Dict, Any, List

class PHIRedactor:
    def __init__(self):
        # Common PHI patterns
        self.patterns = {
            "SSN": r'\b\d{3}-\d{2}-\d{4}\b',
            "DOB": r'\b(0[1-9]|1[0-2])/(0[1-9]|[12]\d|3[01])/(19|20)\d{2}\b',
            "PHONE": r'\b(\+\d{1,2}\s)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b',
            "EMAIL": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "CREDIT_CARD": r'\b(?:\d[ -]*?){13,16}\b'
        }
        
    def redact_text(self, text: str) -> str:
        """Redact PHI from a string."""
        if not isinstance(text, str):
            return text
            
        for label, pattern in self.patterns.items():
            text = re.sub(pattern, f"[REDACTED_{label}]", text)
        return text

    def redact_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively redact PHI from a dictionary."""
        redacted = {}
        for key, value in data.items():
            if isinstance(value, str):
                redacted[key] = self.redact_text(value)
            elif isinstance(value, dict):
                redacted[key] = self.redact_dict(value)
            elif isinstance(value, list):
                redacted[key] = [self.redact_dict(v) if isinstance(v, dict) else self.redact_text(v) if isinstance(v, str) else v for v in value]
            else:
                redacted[key] = value
        return redacted

if __name__ == "__main__":
    redactor = PHIRedactor()
    sample = {
        "user": "John Doe",
        "message": "My SSN is 123-45-6789 and my email is john@example.com",
        "metadata": {
            "birth_date": "05/12/1985"
        }
    }
    print("Original:", sample)
    print("Redacted:", redactor.redact_dict(sample))
