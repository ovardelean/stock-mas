import json, sys, os, time
import random

class RandAlgorithm(object):
    def __init__(self):
        self.name = "RAND"
        random.seed(time.time())
        pass

    def predict_prices(self, train_dates, train_prices, predictions):
        return [random.uniform(min(train_prices), max(train_prices)) for i in range(0, predictions)]