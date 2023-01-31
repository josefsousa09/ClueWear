import circuitpython_csv as csv
from ulab import numpy as np

class CsvHelpers():
    def __init__(self) -> None:
        pass
    def save_calibration_data(self,data):
        with open("movement_data.csv", mode="w", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(['x','y','z','movement_type'])
            writer.writerows(data)
        print("DONE")
    