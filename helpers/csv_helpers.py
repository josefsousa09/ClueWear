import circuitpython_csv as csv
from ulab import numpy as np
import time


class CsvHelpers():
    def __init__(self) -> None:
        pass

    def seperate_labels_and_data(self,dataset):
        data = []
        labels = []
        for row in dataset:
            data.append([float(x) for x in row[:3]])
            time.sleep(0.2)
            labels.append(int(row[3]))
            time.sleep(0.5)
        return data, labels

    def write_to_file(self,filename, data):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)

    def create_dataset(self,filename):
        dataset = []
        with open(filename, mode="r") as file:
            reader = csv.reader(file)
            for line in reader:
                dataset.append(line)
                time.sleep(0.5)
            return dataset

    def save_calibration_data(self,filename, movement_data):
        self.write_to_file(filename, movement_data)

    def chunked_X_train_generator(self,X_train):
        return np.array(X_train)
        
