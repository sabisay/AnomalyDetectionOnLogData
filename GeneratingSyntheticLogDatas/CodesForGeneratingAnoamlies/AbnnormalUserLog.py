import pandas as pd
import os
import numpy as np

# Read the existing dataset
file_path = r"./AnomalyAddedGeneration/Test_AbnormalHours_AbnormalAccessDuration.csv"
df = pd.read_csv(file_path)

# Ensure timestamp is in datetime format
df['Timestamp'] = pd.to_datetime(df['Timestamp'])

# Select 3 random users
selected_users = np.random.choice(df["UserID"].unique(), 3, replace=False)

abnormal_rows = []
remaining_rows = []

for user in selected_users:
    user_logs = df[df["UserID"] == user].copy()
    
    # Pick the most accessed patient
    target_patient = user_logs["PatientID"].value_counts().idxmax()
    
    # Select 70% of the user's logs for modification
    num_to_modify = int(len(user_logs) * 0.8)
    modify_indices = np.random.choice(user_logs.index, num_to_modify, replace=False)
    
    # Modify 70% of rows to access the same patient
    user_logs.loc[modify_indices, "PatientID"] = target_patient  
    
    # Shift timestamps closer together
    base_time = user_logs["Timestamp"].min()
    user_logs.loc[modify_indices, "Timestamp"] = [
        base_time + pd.Timedelta(minutes=np.random.randint(2, 5)) for _ in range(num_to_modify)
    ]
    
    abnormal_rows.append(user_logs.loc[modify_indices])
    remaining_rows.append(user_logs.drop(index=modify_indices))

# Create DataFrame for abnormal rows
abnormal_df = pd.concat(abnormal_rows)
remaining_df = pd.concat(remaining_rows)

# Update the main dataset (keeping 30% of modified users' logs)
df = df[~df["UserID"].isin(selected_users)]  # Remove all logs of selected users first
df = pd.concat([df, remaining_df])  # Add back the 30% remaining logs

# Generate new file name and save the modified dataset
os.makedirs("./AnomalyAddedGeneration", exist_ok=True)
new_file_path = f"./AnomalyAddedGeneration/Test_AbnormalLogs.csv"
df.to_csv(new_file_path, index=False)

# Save anomalous rows separately
abnormal_file_path = "./AnomalyAddedGeneration/Test_AbnormalRows.csv"
if os.path.exists(abnormal_file_path):
    abnormal_df.to_csv(abnormal_file_path, mode='a', header=False, index=False)  # Append if file exists
else:
    abnormal_df.to_csv(abnormal_file_path, index=False)  # Create a new file

print(f"Modified dataset saved: {new_file_path}")
print(f"Anomalous rows added: {abnormal_file_path}")