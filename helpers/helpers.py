import circuitpython_csv as csv
from ulab import numpy as np
import time


class Helpers():
    def __init__(self) -> None:
        pass

    def write_to_file(self,filename, data):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def create_dataset(self,filename):
        data = []
        labels = []
        with open(filename, mode="r") as file:
            reader = csv.reader(file)
            for line in reader:
                data.append([float(x) for x in line[:3]])
                time.sleep(0.1)
                labels.append(int(line[3]))
            return np.array(data),np.array(labels)

    def organise_data(self,filename):
        data = {}
        with open(filename, mode="r") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[3] in data:
                    data[row[3]].append([float(row[0]), float(row[1]), float(row[2])])
                else:
                    data[row[3]] = []
                    data[row[3]].append([float(row[0]), float(row[1]), float(row[2])])
            return data
        
    def dataset_empty(self,filename):
        with open(filename,mode="r") as file:
            reader = csv.reader(file)
            if not any(reader):
                return True
            else:
                return False

    def save_calibration_data(self,filename, movement_data):
        self.write_to_file(filename, movement_data)