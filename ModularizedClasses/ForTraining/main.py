from Preprocessing import process_all

if __name__ == "__main__":
    process_all(r"GeneratingSyntheticLogDatas\TrdTry\Final\hospital_access_logs.csv", r"GeneratingSyntheticLogDatas\TrdTry\CV\CV.csv", r"GeneratingSyntheticLogDatas\TrdTry\Test\Test.csv", "ModularizedClasses/ForTraining/outputs/")