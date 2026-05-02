import numpy as np
import random

class BiometricsAnalyzer:
    def __init__(self):
        # Simulated "Ideal" typing profile for users
        self.profiles = {
            "employee_04": {"speed": 65, "dwell_time": 0.08, "flight_time": 0.12},
            "admin_user": {"speed": 45, "dwell_time": 0.10, "flight_time": 0.15}
        }

    def verify_session(self, user_id, session_data):
        """
        Verify if session data matches the user's biometric profile.
        session_data: {'speed': float, 'dwell_time': float, 'flight_time': float}
        """
        profile = self.profiles.get(user_id)
        if not profile:
            return {"match": True, "confidence": 0.5, "status": "NEW_USER"}

        # Calculate deviation
        deviations = [
            abs(session_data['speed'] - profile['speed']) / profile['speed'],
            abs(session_data['dwell_time'] - profile['dwell_time']) / profile['dwell_time'],
            abs(session_data['flight_time'] - profile['flight_time']) / profile['flight_time']
        ]
        
        avg_deviation = sum(deviations) / len(deviations)
        confidence = max(0.0, 1.0 - avg_deviation)
        
        return {
            "match": avg_deviation < 0.25,
            "confidence": confidence,
            "status": "VERIFIED" if avg_deviation < 0.25 else "SUSPICIOUS_PATTERN"
        }

    def simulate_capture(self, user_id):
        profile = self.profiles.get(user_id, {"speed": 50, "dwell_time": 0.1, "flight_time": 0.15})
        return {
            "speed": profile["speed"] + random.uniform(-5, 5),
            "dwell_time": profile["dwell_time"] + random.uniform(-0.01, 0.01),
            "flight_time": profile["flight_time"] + random.uniform(-0.02, 0.02)
        }

if __name__ == "__main__":
    analyzer = BiometricsAnalyzer()
    capture = analyzer.simulate_capture("employee_04")
    print(f"Captured: {capture}")
    print(analyzer.verify_session("employee_04", capture))
