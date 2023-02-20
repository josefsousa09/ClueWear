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

    def save_calibration_data(self,filename, movement_data):
        self.write_to_file(filename, movement_data)

    def chunked_X_train_generator(self,X_train):
        return np.array(X_train)
        
