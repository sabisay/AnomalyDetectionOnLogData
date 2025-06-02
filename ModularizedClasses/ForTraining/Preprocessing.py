import pandas as pd
import numpy as np
import os

def get_data(file_path, csv_output_path=None):
    
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(file_path)
    elif ext in [".xlsx", ".xls"]:
        df = pd.read_excel(file_path)
    else:
        raise ValueError("Just csv or xlsx files accepted.")

    if csv_output_path is None:
        csv_output_path = os.path.splitext(file_path)[0] + ".csv"
    df.to_csv(csv_output_path, index=False)
    print(f"Veri CSV olarak kaydedildi: {csv_output_path}")

    return df

def SetDataset(Train, Validation, Test):
    df_train = pd.read_csv(Train)
    df_cv = pd.read_csv(Validation)
    df_test = pd.read_csv(Test)