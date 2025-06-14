import os
import time

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
    print("\n📊 Performance Measurement Started")
    print("=" * 50)
    
    start_time = time.time()
    
    preprocess(trainPath, cvPath, testPath, OutputPath)
    behaviour_analysis(OutputPath, BehvaiourPath)
    model, history = TrainModel(ModelPath, BehvaiourPath)
    
    end_time = time.time()
    total_time = end_time - start_time
    
    plot_training_history(history)
    
    
    print("\n⏱️ Performance Results:")
    print("=" * 50)
    print(f"Total Execution Time: {total_time:.2f} seconds")
    print(f"                     {total_time/60:.2f} minutes")
    print("=" * 50)