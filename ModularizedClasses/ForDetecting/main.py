from Preprocessing import process_all
from BehaviourAnalysis import behaviour_analysis
from TestingModel import DetectAbnormalBehaviour
from keras.models import load_model

inputPath = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\Test\Test.csv"
outputPath = r"ModularizedClasses\ForDetecting\outputs"
behaviourPath = r"ModularizedClasses\ForDetecting\behaviours"

ModelPath = "ModularizedClasses/Model/autoencoder_model.keras"
DataPath = "ModularizedClasses/ForDetecting/behaviours/Test.csv"
Threshold = 0.452005

if __name__ == "__main__":
    process_all(inputPath, outputPath)
    behaviour_analysis(outputPath, behaviourPath)
    
    # Load the model
    autoencod = load_model(ModelPath)
    
    predictions, errors = DetectAbnormalBehaviour(
        model_predictor = autoencod,
        threshold_num=Threshold,
        data_path=DataPath
    )