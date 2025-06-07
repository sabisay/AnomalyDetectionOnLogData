import pandas as pd

# Dosyaları oku
df_labeled = pd.read_csv("Seperated_Anomalies-LabeledDatasets\Test_Final.csv")
df_abnormal = pd.read_csv("Seperated_Anomalies-LabeledDatasets\Test_AbnormalRows.csv")

# 'Label' kolonunu ekle, tüm satırlara 0 yaz
df_labeled['Label'] = 0

# Abnormal ID'leri al
abnormal_ids = df_abnormal['ID'].unique()

# Labeled verisindeki bu ID'lere sahip satırların Label'ını 1 yap
df_labeled.loc[df_labeled['ID'].isin(abnormal_ids), 'Label'] = 1

# Güncellenmiş dosyayı tekrar kaydet (istersen)
df_labeled.to_csv("Seperated_Anomalies-LabeledDatasets\Test_Labeled.csv", index=False)