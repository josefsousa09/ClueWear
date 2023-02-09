import circuitpython_csv as csv
from ulab import numpy as np
import time


class CsvHelpers():
    def __init__(self) -> None:
        pass

    def seperate_labels_and_data(self,dataset):
        data = np.empty((len(list(dataset)), 3))
        labels = np.empty(len(list(dataset)))
        for i, row in enumerate(dataset):
            data[i, :] = [float(x) for x in row[:3]]
            labels[i] = int(row[3])

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
                time.sleep(0.1)
                if len(dataset) >= 1000:
                    yield dataset
                    dataset = []
        if dataset:
            yield dataset

    def save_calibration_data(self,filename, movement_data):
        self.write_to_file(filename, movement_data)
