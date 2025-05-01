import pandas as pd
import random

def datasetDividor(input_file, n, output_selected, output_remaining):
    # Read the dataset
    df = pd.read_csv(input_file)
    
    # Ensure n is not greater than the total number of records
    if n > len(df):
        raise ValueError("n is larger than the dataset size!")
    
    # Randomly select n rows
    selected_indices = random.sample(range(len(df)), n)
    selected_rows = df.iloc[selected_indices]
    remaining_rows = df.drop(selected_indices)
    
    # Save to new CSV files
    selected_rows.to_csv(output_selected, index=False)
    remaining_rows.to_csv(output_remaining, index=False)
    
    print(f"Extracted {n} lines to {output_selected} and saved remaining lines to {output_remaining}.")

# Example usage
datasetDividor(r"./FirstGeneration/CV_Test_Combine.csv", 20000, r"./FirstGeneration/Test.csv", r"./FirstGeneration/CV.csv")