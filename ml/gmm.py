from ulab import numpy as np
from helpers.helpers import Helpers

class GMM():
    def __init__(self) -> None:
        self.helpers = Helpers()
        self.expected = {}
        self.cov = {}

    def train(self):
        data = self.helpers.organise_data("profiles/profile_1_data.csv")
        for gesture, X in data.items():
            self.expected[gesture] = self.avg(X)
            self.cov[gesture] = self.cov_matrix(X, self.expected[gesture])
        data = None

    def avg(self, X):
        n = len(X)
        if n < 1:
            return (0, 0)

        x_total = 0
        y_total = 0
        z_total = 0
        for point in X:
            x_total += point[0]
            y_total += point[1]
            z_total += point[2]

        return (x_total/n, y_total/n, z_total/n)

    def cov_matrix(self, X, expected):
        X1 = [point[0] for point in X]
        X2 = [point[1] for point in X]
        X3 = [point[2] for point in X]

        var11 = self.variance(X1, expected[0])
        var12 = self.covariance(X1, X2, expected[0], expected[1])
        var13 = self.covariance(X1, X3, expected[0], expected[2])
        var21 = self.covariance(X2, X1, expected[1], expected[0])
        var22 = self.variance(X2, expected[1])
        var23 = self.covariance(X2, X3, expected[1], expected[2])
        var31 = self.covariance(X3, X1, expected[2], expected[0])
        var32 = self.covariance(X3, X2, expected[2], expected[1])
        var33 = self.variance(X3, expected[2])

        return [[var11, var12, var13], [var21, var22, var23], [var31, var32, var33]]
    
    def covariance(self, X, Y, Ex, Ey):
        n = len(X)
        if n <= 1:
            return 0
        total = 0
        for x , y in zip(X,Y):
            total += (x - Ex) * (y - Ey)

        return total / (n - 1)

    def variance(self,X,Ex):
        n = len(X)
        if n <= 1:
            return 0

        total = 0
        for x in X:
            total += (x - Ex)**2

        return total / (n - 1)

    def pdf_classifier(self, x):
        mPdf = -1
        mGesture = '?'
        
        for gesture, E in self.expected.items():
            diff = np.array([x[i] - E[i] for i in range(3)])
            inv = self.gauss_jordan_elimination(self.cov[gesture])
            det = self.determinant(self.cov[gesture])
            tmp = self.matrix_mult(diff,inv)
            pdf = (1 / (2 * 3.14**1.5 * det**0.5)) * 2.718 **tmp 

            if pdf > mPdf:
                mPdf = pdf
                mGesture = gesture

        return mGesture, mPdf

    def determinant(self, M):
        return M[0][0] * (M[1][1]*M[2][2] - M[1][2]*M[2][1]) - M[0][1] * (M[1][0]*M[2][2] - M[1][2]*M[2][0]) + M[0][2] * (M[1][0]*M[2][1] - M[1][1]*M[2][0])

    def matrix_mult(self,diff,inv):
        tmp = 0
        for i in range(3):
            for j in range(3):
                tmp += diff[i] * inv[i][j] * diff[j]
        tmp *= -0.5
        return tmp
        

    def gauss_jordan_elimination(self, M):
    # Create an identity matrix of the same size as M
        identity = np.eye(len(M))

        # Combine M with the identity matrix
        augmented = np.zeros((len(M), 2 * len(M)))
        augmented[:, :len(M)] = M
        augmented[:, len(M):] = identity

        # Perform Gauss-Jordan elimination to transform M into the identity matrix
        for i in range(len(M)):
            # Swap rows if necessary to get a nonzero diagonal element
            if augmented[i][i] == 0:
                for j in range(i + 1, len(M)):
                    if augmented[j][i] != 0:
                        augmented[i], augmented[j] = augmented[j], augmented[i]
                        break
                    
            # Scale the row to make the diagonal element equal to 1
            diagonal_element = augmented[i][i]
            augmented[i] = augmented[i] / diagonal_element

            # Subtract a multiple of the row from other rows to make their elements zero
            for j in range(len(M)):
                if j != i:
                    factor = augmented[j][i] / augmented[i][i]
                    augmented[j] = augmented[j] - factor * augmented[i]

        # The right half of the augmented matrix is now the inverse of M
        inverse = augmented[:, len(M):]

        return inverse

    
    