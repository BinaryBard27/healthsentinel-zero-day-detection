import sys
import numpy as np
import logging
import torch
import traceback

logging.basicConfig(level=logging.INFO)
sys.path.append('c:/Users/SHERWIN/OneDrive/Documents/Desktop/project/HealthSentinel/ai_backend')

from ai_server import model_manager

def test_models():
    print("Loading all models...")
    model_manager.load_all_models()
    
    print("\n" + "="*40)
    print("--- Ransomware ---")
    if model_manager.ransomware_models:
        try:
            rf = model_manager.ransomware_models['rf']
            scaler = model_manager.ransomware_models['scaler']
            n_feat = getattr(scaler, 'n_features_in_', getattr(scaler, 'n_features_', 12)) 
            fake_data = np.random.rand(1, n_feat)
            scaled = scaler.transform(fake_data)
            out = rf.predict(scaled)
            print(f"Ransomware Success! (features={n_feat}) Model Output: {out}")
        except Exception as e:
            print(f"Ransomware Exception: {e}")
            traceback.print_exc()
    else:
        print("Ransomware model DID NOT LOAD.")
        
    print("\n" + "="*40)
    print("--- Phishing ---")
    if model_manager.phishing_system:
        try:
            email = {'sender': 'test@test.com', 'subject': 'hello', 'message': 'test', 'urls': []}
            out = model_manager.phishing_system.analyze_email(email)
            print(f"Phishing Success! Model Output: {out}")
        except Exception as e:
            print(f"Phishing Exception: {e}")
            traceback.print_exc()
    else:
        print("Phishing model DID NOT LOAD.")
        
    print("\n" + "="*40)
    print("--- SQL Injection ---")
    if model_manager.sql_injection_model:
        try:
            tok = model_manager.sql_injection_model['tokenizer']
            mod = model_manager.sql_injection_model['model']
            inp = tok("SELECT * FROM users", padding='max_length', truncation=True, max_length=64, return_tensors='pt')
            with torch.no_grad():
                out = mod(**inp)
            print(f"SQL Injection Success! Model Output Shape: {out.logits.shape}")
        except Exception as e:
            print(f"SQL Injection Exception: {e}")
            traceback.print_exc()
    else:
        print("SQL Injection DID NOT LOAD.")
        
    print("\n" + "="*40)
    print("--- Insider Threat (LSTM) ---")
    if model_manager.lstm_model is not None:
        try:
            if isinstance(model_manager.lstm_model, dict):
                print("LSTM is loaded as a state_dict (will use statistical fallback).")
            else:
                print("LSTM is a full model object. Testing inference...")
                import torch
                fake_seq = torch.randn(1, 60, 64) # Example shape
                try:
                    if hasattr(model_manager.lstm_model, 'get_reconstruction_error'):
                        err = model_manager.lstm_model.get_reconstruction_error(fake_seq)
                        print(f"   Success! Reconstruction Error Method: {err}")
                    else:
                        out = model_manager.lstm_model(fake_seq)
                        print(f"   Success! Inference shape: {out.shape}")
                except Exception as e:
                    print(f"   Warning: Inference failed using shape (1,60,64). Trying shape (1,10,12)...")
                    fake_seq_12 = torch.randn(1, 10, 12)
                    out = model_manager.lstm_model(fake_seq_12)
                    print(f"   Success! Inference shape: {out.shape} or reconstruction error computed.")
        except Exception as e:
            print(f"LSTM Exception: {e}")
            traceback.print_exc()
    else:
        print("LSTM model DID NOT LOAD.")
    
    print("\nDone testing.")

if __name__ == '__main__':
    test_models()
