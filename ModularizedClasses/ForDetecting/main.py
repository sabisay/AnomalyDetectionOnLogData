import pandas as pd
from Preprocessing import process_all
from BehaviourAnalysis import behaviour_analysis
from TestingModel import DetectAbnormalBehaviour
from keras.models import load_model
from Evaluation import create_comparison_df, evaluate_model_performance
from SecondPhase import explain_anomalies

input = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\Test\Test.csv"
Model = r"ModularizedClasses\Model\autoencoder_model.keras"
Label = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\Test\Test_AnomalousUsers.txt"

outputPath = r"ModularizedClasses\ForDetecting\outputs"
behaviourPath = r"ModularizedClasses\ForDetecting\behaviours"
userPath = r"ModularizedClasses\ForDetecting\users"

Threshold = 0.452005

if __name__ == "__main__":
    process_all(input, outputPath)
    behaviour_analysis(outputPath, behaviourPath, userPath)
    
    # Load the model
    autoencod = load_model(Model)
    
    predictions, errors, abnormal_users = DetectAbnormalBehaviour(
        model_predictor = autoencod,
        threshold_num=Threshold,
        data_path= behaviourPath + r"\Test_processed.parquet",
        raw_df_path= userPath + r"\Test_processed_raw.parquet"
    )
    
    # Get true labels from file
    # Remove duplicates from abnormal_users
    abnormal_users = list(set(abnormal_users))
    # Debug print
    print("\nDetected Abnormal Users:")
    print(f"Total count: {len(abnormal_users)}")
    for i, user in enumerate(abnormal_users, 1):
        print(f"{i}. {user}")
    y_true = []
    with open(Label, 'r') as f:
        y_true = [line.strip() for line in f]
        
    comparison_df = create_comparison_df(y_true, abnormal_users)
    evaluate_model_performance( comparison_df['Label'], comparison_df['DetectedAbnormal'])
    