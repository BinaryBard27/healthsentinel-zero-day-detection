import random
import time
from datetime import datetime

class AttackSimulator:
    def __init__(self):
        self.attack_stages = [
            "Reconnaissance",
            "Exploitation",
            "Lateral Movement",
            "Action on Objective"
        ]
        
    def generate_log(self, stage, user_id="employee_04"):
        timestamp = datetime.utcnow().isoformat() + "Z"
        
        if stage == "Reconnaissance":
            return {
                "timestamp": timestamp,
                "user": user_id,
                "event_type": "network_scan",
                "source_ip": f"192.168.1.{random.randint(2, 254)}",
                "target_range": "10.0.0.0/24",
                "protocol": "TCP",
                "ports": [80, 443, 22, 3389, 445],
                "honeypot_interaction": random.choice([True, False, False, False]) # 25% chance of hitting honeypot early
            }
            
        elif stage == "Exploitation":
            return {
                "timestamp": timestamp,
                "user": user_id,
                "event_type": "process_start",
                "process_name": random.choice(["powershell.exe", "cmd.exe", "bash"]),
                "cmdline": "powershell -ExecutionPolicy Bypass -WindowStyle Hidden -EncodedCommand " + "A" * 50,
                "parent_process": "winword.exe",
                "privilege_escalation_attempt": True
            }
            
        elif stage == "Lateral Movement":
            return {
                "timestamp": timestamp,
                "user": user_id,
                "event_type": "remote_login",
                "source_host": "WS-EMP-04",
                "target_host": "SRV-PATIENT-DB",
                "auth_method": "NTLM",
                "status": "success",
                "sequence_length": random.randint(5, 15)
            }
            
        elif stage == "Action on Objective":
            return {
                "timestamp": timestamp,
                "user": user_id,
                "event_type": "file_access",
                "file_count": random.randint(100, 500),
                "operation": "compress_and_encrypt",
                "extension": ".crypt",
                "entropy": 7.8,
                "data_volume_mb": random.uniform(50, 200)
            }
            
        return {"error": "Invalid attack stage"}

    def get_kill_chain(self, user_id="employee_04"):
        """Returns a sequence of events representing a full attack."""
        chain = []
        for stage in self.attack_stages:
            chain.append(self.generate_log(stage, user_id))
        return chain

if __name__ == "__main__":
    simulator = AttackSimulator()
    print("Generating sample kill chain...")
    for event in simulator.get_kill_chain():
        print(f"--- {event.get('event_type')} ---")
        print(event)
        print()
