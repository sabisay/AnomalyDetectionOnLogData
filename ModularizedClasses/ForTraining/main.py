from Preprocessing import preprocess
from BehaviourAnalysis import behaviour_analysis
from TrainingModel import TrainModel, plot_training_history

trainPath = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\Final\hospital_access_logs.csv"
cvPath = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\CV\CV.csv"
testPath = r"DatasetGenerator\GeneratingSyntheticLogDatas\TrdTry\Test\Test.csv"

OutputPath = "ModularizedClasses/ForTraining/outputs/"
BehvaiourPath = "ModularizedClasses/ForTraining/behaviours/"
ModelPath = "ModularizedClasses/Model/"

if __name__ == "__main__":
    preprocess(trainPath, cvPath, testPath, OutputPath)
    behaviour_analysis(OutputPath, BehvaiourPath)
    model, history = TrainModel(ModelPath, BehvaiourPath)
    plot_training_history(history)