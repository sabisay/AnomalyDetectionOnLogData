import pandas as pd
import random

def combine_and_shuffle_datasets(input_file_1, input_file_2, output_combined):
    # Read the two datasets
    df1 = pd.read_csv(input_file_1)
    df2 = pd.read_csv(input_file_2)
    
    # Concatenate the two datasets
    combined_df = pd.concat([df1, df2], ignore_index=True)
    
    # Shuffle the combined dataset randomly
    combined_df = combined_df.sample(frac=1, random_state=random.seed()).reset_index(drop=True)
    
    # Save the shuffled combined dataset to a new CSV file
    combined_df.to_csv(output_combined, index=False)
    
    print(f"Combined and shuffled dataset saved to {output_combined}.")

# Example usage
combine_and_shuffle_datasets(".\To_Combine\Test_AbnormalLogs_Modified.csv", ".\AnomalyAddedGeneration\Test_AbnormalRows.csv", ".\Final\Test_Final.csv")