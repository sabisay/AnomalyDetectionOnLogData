import pandas as pd

# Ana veri dosyası
cv_path = r"./GeneratingSyntheticLogDatas/SecondTry/Test/Test.csv"
output_labeled_path = r"./GeneratingSyntheticLogDatas/SecondTry/Test/Test_Labeled.csv"

# Anomali dosyaları
anomaly_files = [
    r"./GeneratingSyntheticLogDatas/SecondTry/Test/Test_AbnormalAccessDuration.csv",
    r"./GeneratingSyntheticLogDatas/SecondTry/Test/Test_DuplicateTimestempAnomaly.csv",
    r"./GeneratingSyntheticLogDatas/SecondTry/Test/Test_VPNAccessAnomaly.csv",
    r"./GeneratingSyntheticLogDatas/SecondTry/Test/Test_SameTimestempSamePatientAnomaly.csv",
]

# Ana veriyi yükle
df = pd.read_csv(cv_path)

# Tüm anormal ID'leri topla
anomalous_ids = set()

for file in anomaly_files:
    if not pd.read_csv(file).empty:
        anomaly_df = pd.read_csv(file)
        anomalous_ids.update(anomaly_df["ID"].astype(str).tolist())

# ID'leri string yap, karşılaştırma için
df["ID"] = df["ID"].astype(str)

# Label kolonu ekle
df["Label"] = df["ID"].apply(lambda x: 1 if x in anomalous_ids else 0)

# Yeni dosyayı kaydet
df.to_csv(output_labeled_path, index=False)

print(f"Labeled dosya başarıyla oluşturuldu: {output_labeled_path}")
print(f"Toplam anormal kayıt sayısı: {df['Label'].sum()}")
