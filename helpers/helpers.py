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
        with open(filename, mode='r') as file:
            reader = csv.reader(file)
            for row in reader:
                label = row[3]
                if label in data:
                    data[label].append([float(row[0]), float(row[1]), float(row[2])])
                else:
                    data[label] = [[float(row[0]), float(row[1]), float(row[2])]]
            return data
        
    def dataset_empty(self,filename):
        with open(filename,mode='r') as file:
            reader = csv.reader(file)
            if sum(1 for row in reader) == 0:
                return True
            else:
                return False

    def read_config_file(self):
        config = {}
        with open("config.txt",mode='r') as file:
            for line in file:
                if line.strip():
                    name, value = line.strip().split('=')
                    if value.isdigit():
                        value = int(value)
                    elif value.lower() == 'on':
                        value = True
                    elif value.lower() == 'off':
                        value = False
                    config[name] = value
        return config
    
    def update_config_file(self,config_dict):
        with open("config.txt", mode='r') as file:
            lines = file.readlines()
        updated_lines = []
        for line in lines:
            if line.strip():
                name, value = line.strip().split('=')
                if name in config_dict:
                    new_value = config_dict[name]
                    if isinstance(new_value,bool):
                        value = 'ON' if new_value else 'OFF'
                    else:
                        value = str(new_value)
                    line = f"{name}={value}\n"
            updated_lines.append(line)

        with open("config.txt", 'w') as file:
            for i in updated_lines:
                file.write(i)