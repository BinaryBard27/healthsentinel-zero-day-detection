import sys
import logging
logging.basicConfig(level=logging.ERROR)
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')
from ai_server import model_manager
import torch

model_manager._load_sql_injection_model()
tokenizer = model_manager.sql_injection_model['tokenizer']
model = model_manager.sql_injection_model['model']

queries = [
    "SELECT * FROM users",
    "SELECT * FROM users WHERE username = 'admin' OR '1'='1' -- AND password = 'x'",
    "DROP TABLE users;"
]

for q in queries:
    inputs = tokenizer(q, padding='max_length', truncation=True, max_length=512, return_tensors='pt')
    with torch.no_grad():
        outputs = model(**inputs)
        probs = torch.softmax(outputs.logits, dim=1)
        pred = torch.argmax(probs, dim=1).item()
    print(f"Query: {q}")
    print(f"Probs: {probs.tolist()[0]}")
    print(f"Pred: {pred}")
    print('-'*40)
