import pandas as pd
from Preprocessing import process_all
from BehaviourAnalysis import behaviour_analysis, load_datasets
from TestingModel import DetectAbnormalBehaviour
from keras.models import load_model

input = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\Test\Test.csv"
Model = r"ModularizedClasses\Model\lstm_autoencoder_model.keras"

outputPath = r"ModularizedClasses\ForDetecting\outputs"
behaviourPath = r"ModularizedClasses\ForDetecting\behaviours"
userPath = r"ModularizedClasses\ForDetecting\users"

Threshold = 0.452005

if __name__ == "__main__":
    process_all(input, outputPath)
    behaviour_analysis(outputPath, behaviourPath, userPath)
    
    # Load the model
    autoencod = load_model(Model)
    
    predictions, errors = DetectAbnormalBehaviour(
        model_predictor = autoencod,
        threshold_num=Threshold,
        data_path= behaviourPath + r"\Test_processed.parquet",
        raw_df_path= userPath + r"\Test_processed_raw.parquet"
    )