"""
Third-Party App Security - Static Analysis Tool
==============================================
Analyzes third-party Python apps/scripts before they are allowed 
to connect to the HealthSentinel ecosystem.

Checks for:
1. Sensitive strings (API keys, IP addresses)
2. Dangerous imports (os, subprocess, socket)
3. Known malicious patterns
4. Permission manifest validation
"""

import ast
import os
import re
import hashlib
from typing import List, Dict, Any

class StaticAnalyzer:
    def __init__(self):
        self.dangerous_imports = ['os', 'subprocess', 'socket', 'pickle', 'shutil', 'requests', 'urllib']
        self.sensitive_patterns = [
            r'api[_-]key\s*=\s*["\'][a-zA-Z0-9]{16,}["\']',
            r'password\s*=\s*["\'][a-zA-Z0-9]{8,}["\']',
            r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}', # IP Address
            r'exec\(',
            r'eval\('
        ]

    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """Performs static analysis on a single Python file."""
        if not os.path.exists(file_path):
            return {"error": "File not found"}

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        results = {
            "filename": os.path.basename(file_path),
            "sha256": hashlib.sha256(content.encode()).hexdigest(),
            "issues": [],
            "risk_score": 0.0,
            "status": "APPROVED"
        }

        # 1. AST Analysis for imports and dangerous calls
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                # Check imports
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names if isinstance(node, ast.Import) else [node.module]:
                        name = alias.name if isinstance(node, ast.Import) else node.module
                        if name in self.dangerous_imports:
                            results["issues"].append({
                                "type": "DANGEROUS_IMPORT",
                                "detail": f"Import of sensitive module: {name}",
                                "severity": "medium"
                            })
                            results["risk_score"] += 0.2

                # Check for exec/eval
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name) and node.func.id in ['exec', 'eval']:
                        results["issues"].append({
                            "type": "DANGEROUS_CALL",
                            "detail": f"Use of {node.func.id}()",
                            "severity": "high"
                        })
                        results["risk_score"] += 0.5

        except Exception as e:
            results["issues"].append({"type": "PARSING_ERROR", "detail": str(e), "severity": "medium"})

        # 2. String Pattern Matching for secrets/IPs
        for pattern in self.sensitive_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                results["issues"].append({
                    "type": "SENSITIVE_STRING",
                    "detail": f"Found sensitive pattern match: {pattern}",
                    "severity": "medium"
                })
                results["risk_score"] += 0.3

        # Final Status
        if results["risk_score"] >= 0.7:
            results["status"] = "REJECTED"
        elif results["risk_score"] > 0:
            results["status"] = "NEEDS_REVIEW"

        return results

    def validate_manifest(self, manifest: Dict[str, Any]) -> bool:
        """Validates the third-party app permission manifest."""
        required_fields = ["app_name", "vendor", "permissions"]
        if not all(field in manifest for field in required_fields):
            return False
        
        allowed_permissions = ["ehr_read", "ehr_write", "network_out", "device_access"]
        for p in manifest["permissions"]:
            if p not in allowed_permissions:
                return False
        
        return True

if __name__ == "__main__":
    # Example usage
    analyzer = StaticAnalyzer()
    
    # Create a test malicious file
    test_file = "test_third_party.py"
    with open(test_file, "w") as f:
        f.write("import os\nimport socket\napi_key = 'abc123xyz4567890'\ndef attack():\n    exec('print(\"pwned\")')")
    
    report = analyzer.analyze_file(test_file)
    print("--- STATIC ANALYSIS REPORT ---")
    import json
    print(json.dumps(report, indent=2))
    
    # Clean up
    if os.path.exists(test_file):
        os.remove(test_file)
