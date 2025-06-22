import pandas as pd
import os

def load_data(uploaded_file):
    """
    Yüklenen dosyayı uygun formata göre pandas DataFrame olarak okur.
    Noktalı virgül ayracı olan dosyaları da destekler.
    """
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, sep=None, engine='python')  # auto-detect delimiter
        elif uploaded_file.name.endswith(".xlsx"):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Desteklenmeyen dosya formatı."
        return df, None
    except Exception as e:
        return None, f"Dosya okunurken hata oluştu: {str(e)}"


def save_and_forward(uploaded_file):
    if uploaded_file is None:
        return None, None, "Dosya nesnesi alınamadı."
    
    try:
        file_content = uploaded_file.getvalue()

        ext = os.path.splitext(uploaded_file.name)[1].lower()
        save_path = os.path.abspath(f"temp_uploaded{ext}")  # örn: ./temp_uploaded.csv

        # Eğer dosya varsa sil
        if os.path.exists(save_path):
            os.remove(save_path)

        with open(save_path, "wb") as f:
            f.write(file_content)

        return save_path, file_content, None
    except Exception as e:
        return None, None, str(e)
