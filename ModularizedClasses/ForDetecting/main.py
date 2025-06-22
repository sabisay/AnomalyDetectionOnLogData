import os
import numpy as np
from keras.models import load_model
from utils import abnormal_user_detector

possible_extensions = [".csv", ".xlsx"]
input_path = None
for ext in possible_extensions:
    candidate = f"temp_uploaded{ext}"
    if os.path.exists(candidate):
        input_path = candidate
        break

if input_path is None:
    raise FileNotFoundError("No input file found (expected temp_uploaded.csv or temp_uploaded.xlsx)")

model_path = r"ModularizedClasses\Model\autoencoder_model.keras"
output_parquet = r"ModularizedClasses\ForDetecting\outputs\Test_processed.parquet"
threshold = 0.452005

if __name__ == "__main__":
    # Modeli yükle
    model = load_model(model_path)

    # Pipeline'ı çalıştır ve anormal kullanıcıları al
    abnormal_users = abnormal_user_detector(
        input_path=input_path,
        model=model,
        output_parquet=output_parquet,
        threshold=threshold
    )

    # Sonuçları yazdır
    print("\nDetected Abnormal Users:")
    print(f"Total count: {len(abnormal_users)}")
    for i, user in enumerate(abnormal_users, 1):
        print(f"{i}. {user}")