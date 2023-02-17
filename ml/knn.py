from ulab import numpy as np

class KNN():
    def __init__(self) -> None:
        pass

    def euclidean_distance(self,x1, x2):
        distance = 0
        for i in range(len(x1)):
            distance += (x1[i] - x2[i])**2
        return distance**0.5


    def predict(self,X_train,y_train,x_test,k):
        distances = []
        for i in range(len(X_train)):
            distance = self.euclidean_distance(x_test, X_train[i])
            distances.append((distance, y_train[i]))
        distances = sorted(distances, key=lambda x: x[0])[:k]
        labels = [d[1] for d in distances]
        return max(labels, key=labels.count)

    def knn(self,X_train,y_train,X_test,k):
        prediction = self.predict(X_train,y_train,X_test[0],k)
        return prediction
        
    def test(self,X_train,y_train, X_test):
        X_train = np.array([[100, 200], [150, 150], [200, 100]])
        y_train = np.array([0, 1, 2])
        X_test = np.array([[120, 220], [175, 175]])
        k = 3
        predictions = self.knn(X_train, y_train, X_test, k)
        return predictions
        