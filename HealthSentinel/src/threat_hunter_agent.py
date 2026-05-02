import random

class ThreatHunterAgent:
    def __init__(self):
        self.knowledge_base = {
            "ransomware": {
                "explanation": "Ransomware is malicious software that encrypts files and demands payment for decryption. Detection usually occurs via high entropy file operations or suspicious API calls.",
                "remediation": ["Isolate the infected host immediately.", "Disable SMB and RDP if not needed.", "Restore from offline backups."]
            },
            "sql_injection": {
                "explanation": "SQL Injection involves inserting malicious SQL code into input fields to manipulate backend databases. It commonly exploits poorly sanitized inputs.",
                "remediation": ["Use prepared statements (parameterized queries).", "Implement strict input validation.", "Principle of Least Privilege for DB accounts."]
            },
            "phishing": {
                "explanation": "Phishing attempts to trick users into providing sensitive data or clicking malicious links via deceptive emails.",
                "remediation": ["Enable MFA for all users.", "Implement SPF/DKIM/DMARC.", "Conduct regular user awareness training."]
            },
            "insider": {
                "explanation": "Insider threats are risks from individuals within the organization who have authorized access but use it for malicious purposes or out of negligence.",
                "remediation": ["Monitor for unusual data volumes (Egress).", "Implement UBA (User Behavior Analytics).", "Restrict access to sensitive 'Zones'."]
            }
        }

    def query(self, text: str):
        text = text.lower()
        
        # Determine category
        category = "general"
        if "ransom" in text or "encrypt" in text: category = "ransomware"
        elif "sql" in text or "injection" in text or "database" in text: category = "sql_injection"
        elif "phish" in text or "email" in text or "link" in text: category = "phishing"
        elif "insider" in text or "employee" in text or "leak" in text: category = "insider"
        
        if category == "general":
            return {
                "answer": "I am the HealthSentinel Threat Hunter. I can explain security threats and suggest mitigations. Ask me about Ransomware, SQL Injection, Phishing, or Insider Threats.",
                "remediation": []
            }
            
        data = self.knowledge_base[category]
        responses = [
            f"Based on my analysis, {data['explanation']}",
            f"Regarding your query on {category}: {data['explanation']}",
            f"Analysis complete: {data['explanation']}"
        ]
        
        return {
            "answer": random.choice(responses),
            "remediation": data["remediation"]
        }

if __name__ == "__main__":
    agent = ThreatHunterAgent()
    print(agent.query("What should I do about ransomware?"))
