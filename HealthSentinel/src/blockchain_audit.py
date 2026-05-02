import hashlib
import json
import time
from datetime import datetime

class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class BlockchainAudit:
    def __init__(self, storage_path="logs/blockchain_audit.json"):
        self.chain = [self.create_genesis_block()]
        self.storage_path = storage_path
        
    def create_genesis_block(self):
        return Block(0, datetime.utcnow().isoformat(), "Genesis Block - HealthSentinel Audit Trail Started", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_event(self, event_data):
        previous_block = self.get_latest_block()
        new_block = Block(
            len(self.chain),
            datetime.utcnow().isoformat(),
            event_data,
            previous_block.hash
        )
        self.chain.append(new_block)
        self.save_chain()
        return new_block.hash

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

    def save_chain(self):
        try:
            with open(self.storage_path, 'w') as f:
                chain_data = []
                for block in self.chain:
                    chain_data.append({
                        "index": block.index,
                        "timestamp": block.timestamp,
                        "data": block.data,
                        "previous_hash": block.previous_hash,
                        "hash": block.hash
                    })
                json.dump(chain_data, f, indent=2)
        except Exception as e:
            print(f"Error saving blockchain: {e}")

if __name__ == "__main__":
    audit = BlockchainAudit()
    audit.add_event({"type": "ALERT", "severity": "HIGH", "desc": "SQL Injection Detected"})
    audit.add_event({"type": "DLP", "desc": "PHI Redacted in log-402"})
    print(f"Blockchain valid: {audit.is_chain_valid()}")
    print(f"Latest Hash: {audit.get_latest_block().hash}")
