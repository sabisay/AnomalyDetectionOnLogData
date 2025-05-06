import pandas as pd
import numpy as np
import os

# Ayarlanabilir dosya yolları
input_path = r"./GeneratingSyntheticLogDatas/TrdTry/Test/Test.csv"
output_path = r"./GeneratingSyntheticLogDatas/TrdTry/Test/Test.csv"
anomalies_path = r"./GeneratingSyntheticLogDatas/TrdTry/Test/Test_AbnormalAccessDuration.csv"

# Veriyi yükle
df = pd.read_csv(input_path)

# Normal erişim süresi aralığına sahip kullanıcıları filtrele (120-300 sn)
valid_users = (
    df[(df["AccessDuration"] >= 120) & (df["AccessDuration"] <= 300)]
    ["UserID"]
    .value_counts()
    .loc[lambda x: x > 5]  # En az 5 logu olan kullanıcılar
    .index
    .tolist()
)

# Rastgele 3 kullanıcı seç
selected_users = np.random.choice(valid_users, 2, replace=False)

# Anomalileri kaydetmek için index listesi
anomalous_indices = []

# Her kullanıcı için loglarının %20'sine anomali uygula (4000-6000 sn)
for user in selected_users:
    user_logs = df[df["UserID"] == user]
    n_anomalies = max(1, int(len(user_logs) * 0.07))
    anomaly_rows = user_logs.sample(n=n_anomalies, random_state=42)
    
    indices = anomaly_rows.index
    df.loc[indices, "AccessDuration"] = np.random.randint(30, 91, size=n_anomalies)
    anomalous_indices.extend(indices)

# Anormal satırları ayrı kaydet
anomalies_df = df.loc[anomalous_indices]
anomalies_df.to_csv(anomalies_path, mode='a', index=False, header=not os.path.exists(anomalies_path))

# Güncellenmiş tüm veriyi kaydet
df.to_csv(output_path, index=False)

# Değişen satırların ID'lerini yazdır
print("Anomali uygulanan satırların ID'leri:")
print(df.loc[anomalous_indices, "ID"].tolist())

# --- Anomalous UserID'leri kayıt altına al ---
anomalous_user_ids = df.loc[anomalous_indices, "UserID"].unique()
user_tracking_path = r"./GeneratingSyntheticLogDatas/TrdTry/Test/Test_AnomalousUsers.txt"

# Varsa mevcut kullanıcıları oku
if os.path.exists(user_tracking_path):
    with open(user_tracking_path, "r") as f:
        existing_users = set(f.read().splitlines())
else:
    existing_users = set()

# Yeni anomalous kullanıcıları ekle
updated_users = existing_users.union(set(anomalous_user_ids.astype(str)))

# Dosyaya tekrar yaz
with open(user_tracking_path, "w") as f:
    for uid in sorted(updated_users):
        f.write(uid + "\n")