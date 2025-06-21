# frontend/api_utils.py
import os
import requests
import pandas as pd

def post_preprocess_api(df):
    url = "http://localhost/preprocess"   # NGINX üzerinden
    data = {"data": df.to_dict(orient="records")}
    try:
        resp = requests.post(url, json=data, timeout=20)
        if resp.status_code == 200:
            result = resp.json()
            clean_df = pd.DataFrame(result["data"])
            return clean_df, None
        else:
            return None, f"Hata: {resp.text}"
    except Exception as e:
        return None, f"Bağlantı hatası: {e}"
    
def save_uploaded_file_to_disk(uploaded_file, save_path):
    try:
        uploaded_file.seek(0)
        with open(save_path, "wb") as f:
            while True:
                chunk = uploaded_file.read(8192)
                if not chunk:
                    break
                f.write(chunk)
        return True, None
    except Exception as e:
        return False, str(e)

