import json, sys, os, time
import numpy as np
from sklearn.svm import SVR

class SVRAlgorithm(object):
    def __init__(self):
        self.name = "SVR"
        pass

    def predict_prices(self, train_dates, train_prices, predictions):
        train_dates_np = np.reshape([i for i in range(0, len(train_dates))], (len(train_dates), 1))
        svr_rbf = SVR(kernel='rbf', C=10, gamma=0.01)
        svr_rbf.fit(train_dates_np, train_prices)
        predict_dates_np = np.reshape([i for i in range(len(train_dates), predictions+len(train_dates))], (predictions, 1))
        return svr_rbf.predict(predict_dates_np)
