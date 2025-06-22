import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, f1_score, classification_report

from sklearn.preprocessing import StandardScaler

def get_data(file_path, output_path=None):
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".csv":
        try:
            df = pd.read_csv(file_path, encoding="utf-8")
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding="ISO-8859-9")
    
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    
    else:
        raise ValueError("Just csv or xlsx files accepted.")

    if output_path is None:
        output_path = os.path.splitext(file_path)[0] + ".parquet"

    # Klasörü oluştur (varsa hata vermez)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    df.to_parquet(output_path, index=False)
    print(f"Data saved as Parquet: {output_path}")

    
def save_as_parquet(df, name, output_path = None):
    df.to_parquet(name, index=False)  
    
def read_from_parquet(file_path):
    try:
        df = pd.read_parquet(file_path)
        print(f"Data loaded from Parquet: {file_path}")
        return df
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def convert_to_numeric(df):
    # UserID
    if "UserID" in df.columns:
        df["UserID"] = df["UserID"].str.extract(r'USR_(\d+)')
        df['UserID'] = pd.to_numeric(df['UserID'], errors='coerce').astype('Int64')
    
    # Department
    if "Department" in df.columns:
        df['Department'] = df['Department'].str.extract(r'DPT_(\d+)')
        df['Department'] = pd.to_numeric(df['Department'], errors='coerce').astype('Int64')
    
    # UserRole
    if "UserRole" in df.columns:
        df['UserRole'] = df['UserRole'].astype('category').cat.codes
    
    # Connection
    if "Connection" in df.columns:
        df["Connection"] = df["Connection"].astype('category').cat.codes
    
    # AccessLevel
    if "AccessLevel" in df.columns:
        df['AccessLevel'] = df['AccessLevel'].astype('category').cat.codes
    
    # DeviceID
    if "DeviceID" in df.columns:
        df['DeviceID'] = df['DeviceID'].str.extract(r'DVC_(\d+)')
        df['DeviceID'] = pd.to_numeric(df['DeviceID'], errors='coerce').astype('Int64')        
    
    # PatientID
    if "PatientID" in df.columns:
        df['PatientID'] = df['PatientID'].str.extract(r'DVC_(\d+)')
        df['PatientID'] = pd.to_numeric(df['PatientID'], errors='coerce').astype('Int64')
    
    # VisitDepartment
    if "VisitDepartment" in df.columns:
        df['VisitDepartment'] = df['VisitDepartment'].str.extract(r'DPT_(\d+)')
        df['VisitDepartment'] = pd.to_numeric(df['VisitDepartment'], errors='coerce').astype('Int64')
    
    # Timestamp
    if "Timestamp" in df.columns:
        df['Timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce', utc=True)
        if df['Timestamp'].isna().sum() > 0:
            print("Dikkat! Bazı timestamp değerleri parse edilemedi ve NaT oldu.")
        
        df['Year'] = df['Timestamp'].dt.year
        df['Month'] = df['Timestamp'].dt.month
        df['Day'] = df['Timestamp'].dt.day
        df['Hour'] = df['Timestamp'].dt.hour
        df['Minute'] = df['Timestamp'].dt.minute
        df['Second'] = df['Timestamp'].dt.second
        
    return df

def generate_user_behavior_vectors(df, timestamp_col="Timestamp", user_col="UserID"):

    copy_df = df.copy()
    
    print(copy_df.columns.tolist())

    # Parse timestamp and extract date/hour
    copy_df[timestamp_col] = pd.to_datetime(df[timestamp_col])
    copy_df["Date"] = copy_df[timestamp_col].dt.date
    copy_df["Hour"] = copy_df[timestamp_col].dt.hour

    # VPN / Onsite connection ratio
    def vpn_ratio(x):
        return (x == 0).mean()

    # Classify night shift hours
    copy_df["IsNight"] = copy_df["Hour"].apply(
        lambda h: 1 if (h < 7 or h >= 20 or h == 0) else (0 if 9 <= h <= 17 else None)
    )

    # Calculate shift logic: balanced ratio between night and day usage
    def calculate_shift_logic(group):
        total_logs = len(group)
        night_logs = group["IsNight"].sum()
        day_logs = total_logs - night_logs
        night_ratio = night_logs / total_logs
        day_ratio = day_logs / total_logs
        return min(night_ratio, day_ratio)

    # Group by user and date
    grouped = copy_df.groupby([user_col, "Date"])

    # Feature engineering (std_hour was removed)
    session_vectors = grouped.agg(
        total_logs=("ID", "count"),
        mean_duration=("AccessDuration", "mean"),
        fail_ratio=("IsAccessFail", "mean"),
        sensitive_ratio=("IsSensitive", "mean"),
        vpn_ratio=("Connection", vpn_ratio),
        unique_patient_count=("PatientID", pd.Series.nunique),
        unique_device_count=("DeviceID", pd.Series.nunique),
        shift_logic=("IsNight", lambda x: calculate_shift_logic(
            x.to_frame().join(copy_df.loc[x.index, ["Hour"]])
        ))
    ).fillna(0).reset_index()

    return session_vectors

def return_scaled_matrix(df):
    # Get feature names 
    feature_names = [ 'total_logs', 'mean_duration', 'fail_ratio', 'sensitive_ratio',
    'vpn_ratio', 'unique_patient_count', 'unique_device_count', 'shift_logic']
    
    # Drop identifiers before scaling
    X_test = df.drop(columns=["UserID", "Date"])
    X_test = X_test[feature_names]  # Ensure consistent column order
    
    # Use standard scaler to scale each dataset, fit only on training data
    scaler = StandardScaler()
    X_test_scaled = scaler.fit_transform(X_test)
    
    # Return DataFrame with column names
    return pd.DataFrame(X_test_scaled, columns=feature_names)
    
    # Return DataFrame with column names
    return pd.DataFrame(X_test_scaled, columns=feature_names)

def print_abnormal_behaviour_rows(df, predictions, label="Test"):
    # find abnormals
    anomalous_indices = np.where(predictions == 1)[0]
    if len(anomalous_indices) == 0:
        print(f"[{label}] Hiç anomali tespit edilmedi.")
        return
    
    for idx in anomalous_indices:
        row = df.iloc[idx]
        user = row['UserID'] if 'UserID' in row else 'Unknown'
        date = row['Date'] if 'Date' in row else 'Unknown'
        print(f"[{label}] User {user} on {date} marked as anomaly.")

def set_detected_abnormalUsers(df, predictions, label="Test"):
    abnormal_users = []
    anomalous_indices = np.where(predictions == 1)[0]
    
    if len(anomalous_indices) == 0:
        return abnormal_users
    
    for idx in anomalous_indices:
        row = df.iloc[idx]
        user = row['UserID'] if 'UserID' in row else 'Unknown'
        if user != 'Unknown':
            # UserID'yi formatlama
            user_num = int(user)  # String'i integer'a çevir
            if user_num < 10:  # Tek basamaklı
                formatted_user = f"USR_00{user_num}"
            elif user_num < 100:  # İki basamaklı
                formatted_user = f"USR_0{user_num}"
            else:  # Üç basamaklı
                formatted_user = f"USR_{user_num}"
            
            abnormal_users.append(formatted_user)
    
    return list(set(abnormal_users))

def print_results_generalized(total, normal, anomalies, reconstruction_error):
    print("\n" + "="*50)
    print("🔍 ANOMALY DETECTION RESULTS BY LSTM AUTOENCODER")
    print("="*50)
    print(f"📊 Total Sequences: {total}")
    print(f"✅ Normal: {normal} ({(normal/total)*100:.2f}%)")
    print(f"⚠️ Anomalies: {anomalies} ({(anomalies/total)*100:.2f}%)")
    print(f"📈 Average Error: {np.mean(reconstruction_error):.6f}")
    print("="*50 + "\n")
    
##### THIS IS THE METHOD LOADS FILE AND PREPROCESSES IT #####
def load_and_preprocess(input_path, output_parquet=None):
    """
    Loads the file (csv/xlsx), saves as parquet, and returns the processed DataFrame.
    """
    get_data(input_path, output_parquet)
    df = read_from_parquet(output_parquet)
    df = convert_to_numeric(df)
    return df

##### THIS METHOD GENERATES USER BEHAVIOR VECTORS #####
def behavior_analysis(df):
    """
    Generates user behavior vectors and returns both session vectors and scaled matrix.
    """
    session_vectors = generate_user_behavior_vectors(df)
    scaled_matrix = return_scaled_matrix(session_vectors)
    
    return scaled_matrix, session_vectors
    
##### THIS METHOD DETECTS ABNORMAL USERS #####
def model_runner(model, scaled_df, session_vectors, threshold=0.452005):
    """
    Detect abnormal users using a trained autoencoder (LSTM or standard).
    Args:
        model: Trained Keras model (autoencoder)
        scaled_df: DataFrame with scaled features (only features, no UserID/Date)
        session_vectors: DataFrame with original user vectors (UserID, Date, etc.)
        threshold: Threshold for anomaly detection
    Returns:
        test_pred: 0/1 predictions for each row
        reconstruction_error: Reconstruction error for each row
        abnormal_users: List of detected abnormal users (UserID)
    """
    expected_features = [
        'total_logs', 'mean_duration', 'fail_ratio', 'sensitive_ratio',
        'vpn_ratio', 'unique_patient_count', 'unique_device_count', 'shift_logic'
    ]
    if not all(feature in scaled_df.columns for feature in expected_features):
        raise ValueError(f"Missing features. Required: {expected_features}")
    data = scaled_df[expected_features].values.astype('float32')
    input_shape = model.input_shape
    if len(input_shape) == 3:
        print("LSTM model detected - reshaping to 3D")
        data = np.reshape(data, (data.shape[0], 1, data.shape[1]))
    else:
        print("Standard autoencoder detected - using 2D shape")
    print(f"Input data shape after reshape: {data.shape}")
    reconstructed = model.predict(data, verbose=0)
    if len(input_shape) == 3:
        reconstructed = np.reshape(reconstructed, (reconstructed.shape[0], reconstructed.shape[2]))
        data = np.reshape(data, (data.shape[0], data.shape[2]))
    reconstruction_error = np.mean(np.square(data - reconstructed), axis=1)
    test_pred = (reconstruction_error > threshold).astype(int)
    # Find abnormal users (UserID'leri)
    abnormal_users = set_detected_abnormalUsers(session_vectors, test_pred)
    return test_pred, reconstruction_error, abnormal_users
    
##### THIS IS THE METHOD COLLECTS ALL THE ABOVE METHODS AND PRINTS RESULTS #####

def abnormal_user_detector(
    input_path,
    model,
    output_parquet=None,
    threshold=0.452005
):
    """
    Runs the full anomaly detection pipeline and prints results.
    Args:
        input_path: Path to raw csv/xlsx file
        model: Trained Keras model (autoencoder)
        output_parquet: Optional path to save processed parquet
        threshold: Threshold for anomaly detection
    Returns:
        abnormal_users: List of detected abnormal users (UserID)
    """
    # 1. Load and preprocess data
    df = load_and_preprocess(input_path, output_parquet)
    
    # 2. Generate behavior vectors and scaled matrix
    scaled_matrix, session_vectors = behavior_analysis(df)
    
    # 3. Detect abnormal users
    test_pred, reconstruction_error, abnormal_users = model_runner(
        model, scaled_matrix, session_vectors, threshold
    )
    
    # 4. Print results
    total = len(reconstruction_error)
    anomalies = np.sum(test_pred)
    normal = total - anomalies
    print_results_generalized(total, normal, anomalies, reconstruction_error)
    print_abnormal_behaviour_rows(session_vectors, test_pred, label="Test")
    
    print("\nDetected Abnormal Users:")
    print(f"Total count: {len(abnormal_users)}")
    for i, user in enumerate(abnormal_users, 1):
        print(f"{i}. {user}")
    
    return abnormal_users


####### THIS IS VISUALIZATION OF MATRIX #######
def create_comparison_df(y_true, abnormal_users):
    
    # Create user IDs from 1 to 200 with proper formatting
    user_ids = [f"USR_{str(i).zfill(3)}" for i in range(1, 201)]
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame({
        'userID': user_ids,
        'Label': [1 if user in y_true else 0 for user in user_ids],
        'DetectedAbnormal': [1 if user in abnormal_users else 0 for user in user_ids]
    })
    return comparison_df

def evaluate_model_performance(Label, DetectedAbnormal):
    """
    Evaluate model performance using confusion matrix and F1 score
    
    Args:
        Label: True labels (ground truth)
        DetectedAbnormal: Predicted labels from the model
        
    Returns:
        f1: F1 score
        cm: Confusion matrix
    """
    # Calculate confusion matrix
    cm = confusion_matrix(Label, DetectedAbnormal)
    
    # Calculate F1 score
    f1 = f1_score(Label, DetectedAbnormal)
    
    # Print classification report
    print("\nClassification Report:")
    print(classification_report(Label, DetectedAbnormal))
    
    # Plot confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
    plt.title('Confusion Matrix')
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.show()
    
    return f1, cm