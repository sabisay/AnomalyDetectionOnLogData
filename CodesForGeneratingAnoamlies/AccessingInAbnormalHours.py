import pandas as pd
import random
import numpy as np
import os

# Mevcut veri setini oku
file_path = r"./FirstGeneration/CV.csv"
df = pd.read_csv(file_path)

# Convert Timestamp column to datetime
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# Determine users who work mainly in the day (09:00-18:00) or night (20:00-07:00)
day_workers = df[df["Timestamp"].dt.hour.between(9, 18)]["UserID"].unique()
night_workers = df[(df["Timestamp"].dt.hour.between(20, 23)) | (df["Timestamp"].dt.hour.between(0, 7))]["UserID"].unique()

# Randomly pick 10 day workers and 10 night workers
selected_day_users = np.random.choice(day_workers, size=2, replace=False)
selected_night_users = np.random.choice(night_workers, size=1, replace=False)

# Combine selected users
selected_users = list(selected_day_users) + list(selected_night_users)

def flipTime(timestamp):
    """Shift daytime timestamps to nighttime and vice versa."""
    hour = timestamp.hour

    if 9 <= hour <= 18:  # If day, shift to night (00:00 - 07:00)
        new_hour = random.choice(range(0, 7))
    else:  # If night, shift to day (09:00 - 18:00)
        new_hour = random.choice(range(9, 18))

    return timestamp.replace(hour=new_hour)


# Select 2 random rows per chosen user and modify timestamps
modified_rows = df[df["UserID"].isin(selected_users)].groupby("UserID").sample(n=2, random_state=42)
modified_rows["Timestamp"] = modified_rows["Timestamp"].apply(flipTime)
df.loc[modified_rows.index, "Timestamp"] = modified_rows["Timestamp"]

# Remove modified rows from the dataset
df = df.drop(modified_rows.index)

# Generate new file name dynamically
base_name = os.path.splitext(os.path.basename(file_path))[0]  # Extract filename without extension
new_file_path = f"./AnomalyAddedGeneration/{base_name}_AbnormalHours.csv"
df.to_csv(new_file_path, index=False)

# Save abnormal rows, appending to AbnormalRows.csv
abnormal_file_path = "./AnomalyAddedGeneration/CV_AbnormalRows.csv"
if os.path.exists(abnormal_file_path):
    modified_rows.to_csv(abnormal_file_path, mode='a', header=False, index=False)  # Append if file exists
else:
    modified_rows.to_csv(abnormal_file_path, index=False)  # Create new file if not exist

print(f"Modified dataset saved as: {new_file_path}")
print(f"Abnormal rows appended to: {abnormal_file_path}")