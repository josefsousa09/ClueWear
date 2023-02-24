from ulab import numpy as np
from helpers.helpers import Helpers

class GMM():
    helpers = Helpers()
    def __init__(self) -> None:
        pass

    def train(self):
        data = self.helpers.organise_data("profiles/profile_1_data.csv")
        self.expected = {}
        self.cov = {}
        for gesture, X in data.items():
            self.expected[gesture] = self.avg(X)
            self.cov[gesture] = self.cov_matrix(X, self.expected[gesture])

        data = None

    def avg(self, X):
        n = len(X)

        if n < 1:
            return (0, 0)

        x_total = 0
        z_total = 0
        for point in X:
            x_total += point[0]
            z_total += point[1]

        return (x_total/n, z_total)

    def cov_matrix(self, X, expected):

        X1 = []
        X2 = []

        for point in X:
            X1.append(point[0])
            X2.append(point[1])

        var11 = self.variance(X1, expected[0])
        var12 = self.covariance(X1, X2, expected[0], expected[1])
        var21 = self.covariance(X2, X1, expected[1], expected[0])
        var22 = self.variance(X2, expected[1])

        return [[var11, var12], [var21, var22]]


    def covariance(self, X, Y, Ex, Ez):
        n = len(X)

        if n <= 1:
            return 0
        
        total = 0

        for x , z in zip(X,Y):
            total = total + (x - Ex) * (z - Ez)

        return total / (n - 1)


    def variance(self,X,Ex):
        n = len(X)

        if n <= 1:
            return 0

        total = 0

        for x in X:
            total = total + (x - Ex)**2

        return total / (n - 1)

    def pdf_classifier(self, x):
        mPdf = -1
        mGesture = '?'
        
        for gesture, E in self.expected.items():
            det = self.determinant(self.cov[gesture])
            diff = [x[0] - E[0], x[1] - E[1]]
            inv = self.inverse(self.cov[gesture])
            tmp = -0.5 * self.matrix_mult(diff, inv)
            pdf = (1 / (2 * 3.14 * det**0.5)) * 2.718**tmp

            if pdf > mPdf:
                mPdf = pdf
                mGesture = gesture

        return mGesture, mPdf

    def determinant(self, M):
        return (M[0][0] * M[1][1]) - (M[0][1] * M[1][0])

    def inverse(self, M):
        det = self.determinant(M)
        return [[M[1][1]/det, -M[0][1]/det], [-M[1][0]/det, M[0][0]/det]]

    def matrix_mult(self, M1, M2):
        tmp = [M1[0]*M2[0][0] + M1[1]*M2[1][0], M1[0]*M2[0][1] + M1[1]*M2[1][1]]
        return tmp[0]*M1[0] + tmp[1]*M1[1]
