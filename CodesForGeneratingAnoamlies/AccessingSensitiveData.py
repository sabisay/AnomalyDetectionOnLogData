import pandas as pd
import random
import os

# Read the existing dataset
file_path = r"./AnomalyAddedGeneration/CV_AbnormalLogs.csv"
df = pd.read_csv(file_path)

# Define required number of users per role
role_counts = {"Doctor": 2, "Nurse": 1, "Manager": 1}
selected_users = []

# Select users based on role constraints
for role, count in role_counts.items():
    users_in_role = df[df["UserRole"] == role]["UserID"].unique()
    if len(users_in_role) >= count:
        selected_users.extend(random.sample(list(users_in_role), count))
    else:
        selected_users.extend(users_in_role)

# Store modified rows separately before changing the main dataset
modified_rows = pd.DataFrame()

for user in selected_users:
    user_logs = df[df["UserID"] == user].index  # Get log indices for the user
    num_sensitive = int(len(user_logs) * 0.8)  # Set 80% of logs to IsSensitive = 1

    # Randomly select 80% of the user's logs
    sensitive_indices = random.sample(list(user_logs), num_sensitive)
    
    # Update the original dataset
    df.loc[sensitive_indices, "IsSensitive"] = 1
    
    # Store modified rows before making changes
    modified_rows = pd.concat([modified_rows, df.loc[sensitive_indices]])

# Remove modified rows from the dataset
df = df.drop(modified_rows.index)

# Generate new file name dynamically
base_name = os.path.splitext(os.path.basename(file_path))[0]  # Extract filename without extension
new_file_path = f"./To_Combine/{base_name}_Modified.csv"
df.to_csv(new_file_path, index=False)

# Save abnormal rows, appending to AbnormalRows.csv
abnormal_file_path = "./AnomalyAddedGeneration/CV_AbnormalRows.csv"
if os.path.exists(abnormal_file_path):
    modified_rows.to_csv(abnormal_file_path, mode='a', header=False, index=False)  # Append if file exists
else:
    modified_rows.to_csv(abnormal_file_path, index=False)  # Create new file if not exist

print(f"Modified dataset saved as: {new_file_path}")
print(f"Abnormal rows appended to: {abnormal_file_path}")