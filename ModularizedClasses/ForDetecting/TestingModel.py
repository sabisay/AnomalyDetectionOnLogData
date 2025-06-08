import os
import pandas as pd
import numpy as np

def DetectAbnormalBehaviour(model_predictor, threshold_num, data_path):
    # Load the model
    autoencod = model_predictor
    print(f"Model loaded. Expected input shape: {autoencod.input_shape}")
    
    # Load and prepare the data
    df = pd.read_csv(data_path)
    
    # Select only the 8 features the model expects
    expected_features = ['total_logs', 'mean_duration', 'fail_ratio', 'sensitive_ratio',
                        'vpn_ratio', 'unique_patient_count', 'unique_device_count', 'shift_logic']
    
    if not all(feature in df.columns for feature in expected_features):
        raise ValueError(f"Missing features. Required: {expected_features}")
    
    data = df[expected_features].values.astype('float32')
    print(f"Input data shape: {data.shape}")
    
    # Predict using the autoencoder
    reconstructed = autoencod.predict(data, verbose=0)
    
    # Calculate reconstruction error (using numpy arrays)
    reconstruction_error = np.mean(np.square(data - reconstructed), axis=1)
    
    # Identify abnormal behaviours    
    test_pred = (reconstruction_error > threshold_num).astype(int)
    
    # Enhanced visual output
    total = len(reconstruction_error)
    anomalies = np.sum(test_pred)
    normal = total - anomalies
    
    print("\n" + "="*50)
    print("🔍 ANOMALY DETECTION RESULTS")
    print("="*50)
    print(f"📊 Total Sequences: {total}")
    print(f"✅ Normal: {normal} ({(normal/total)*100:.2f}%)")
    print(f"⚠️ Anomalies: {anomalies} ({(anomalies/total)*100:.2f}%)")
    print(f"📈 Average Error: {np.mean(reconstruction_error):.6f}")
    print("="*50 + "\n")
    
    return test_pred, reconstruction_error