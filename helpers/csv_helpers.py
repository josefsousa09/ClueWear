import circuitpython_csv as csv
from ulab import numpy as np
import time
class CsvHelpers():
    def __init__(self) -> None:
        pass
    def save_calibration_data(self,data):
        with open("movement_data.csv", mode="w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerows(data)
    
    def import_data(self):
        dataset = []
        with open("movement_data.csv", mode="r") as file:
            reader = csv.reader(file)
            for line in reader:
                dataset.append(line)
                time.sleep(0.1)
        return dataset
