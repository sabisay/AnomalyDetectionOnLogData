import random
import pandas as pd
import os

# Read the existing dataset
file_path = r"./AnomalyAddedGeneration/CV_AbnormalHours.csv"
df = pd.read_csv(file_path)

# Select 8 random unique users (5 high access + 3 low access)
random_users = random.sample(df["UserID"].unique().tolist(), 5)
high_duration_users = random_users[:2]  # First 5 users will get high access duration
low_duration_users = random_users[2:]   # Last 3 users will get low access duration

# Create an empty DataFrame to store modified rows
modified_rows = pd.DataFrame(columns=df.columns)

# Assign high access duration (> 60 seconds) to selected users
for user in high_duration_users:
    user_indices = df[df["UserID"] == user].index.tolist()
    if len(user_indices) < 30:
        continue  # Skip if insufficient entries
    
    # Randomly select 5 to 8 entries
    num_changes = random.randint(8, 15)
    high_indices = random.sample(user_indices, min(len(user_indices), num_changes))
    df.loc[high_indices, "AccessDuration"] = [random.randint(61, 120) for _ in high_indices]
    
    # Save selected rows
    modified_rows = pd.concat([modified_rows, df.loc[high_indices]], ignore_index=True)

# Assign low access duration (< 30 seconds) to selected users
for user in low_duration_users:
    user_indices = df[df["UserID"] == user].index.tolist()
    if len(user_indices) < 2:
        continue  # Skip if insufficient entries
    
    # Randomly select 5 to 8 entries
    num_changes = random.randint(5, 8)
    low_indices = random.sample(user_indices, min(len(user_indices), num_changes))
    df.loc[low_indices, "AccessDuration"] = [random.randint(5, 29) for _ in low_indices]
    
    # Save selected rows
    modified_rows = pd.concat([modified_rows, df.loc[low_indices]], ignore_index=True)

# Remove anomalous rows from the main dataset
df = df.drop(modified_rows.index, errors='ignore')

# Generate new file name and save the dataset
os.makedirs("./AnomalyAddedGeneration", exist_ok=True)
base_name = os.path.splitext(os.path.basename(file_path))[0]  # Get file name without extension
new_file_path = f"./AnomalyAddedGeneration/{base_name}_AbnormalAccessDuration.csv"
df.to_csv(new_file_path, index=False)

# Save anomalous rows
abnormal_file_path = "./AnomalyAddedGeneration/CV_AbnormalRows.csv"
if os.path.exists(abnormal_file_path):
    modified_rows.to_csv(abnormal_file_path, mode='a', header=False, index=False)  # Append if file exists
else:
    modified_rows.to_csv(abnormal_file_path, index=False)  # Create a new file

print(f"Modified dataset saved: {new_file_path}")
print(f"Anomalous rows added: {abnormal_file_path}")