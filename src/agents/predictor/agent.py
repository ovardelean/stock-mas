import time, datetime
import logging

import config

from agents.predictor.svr import SVRAlgorithm
from agents.predictor.rand import  RandAlgorithm
from database.elasticsearch_db import EsDatabase
from utils.logger import create_logger


class Predictor(object):
    def __init__(self):
        self.database = EsDatabase()
        self.algorithms = [
                            SVRAlgorithm(),
                            RandAlgorithm(),
                        ]
        self.tickers = config.TICKERS
        self.logger = create_logger('Predictor')

    def predict(self, algorithm, train_data):
        train_data = sorted(train_data, key=lambda k: k['_source']['timestamp'])
        train_dates, train_prices = [], []
        for item in train_data:
            train_dates.append(item['_source']['timestamp'])
            train_prices.append(item['_source']['market_data']['open'])

        predicted_prices = algorithm.predict_prices(train_dates,train_prices,config.PREDICT_SIZE)
        return predicted_prices

    def generate_predicted_data(self, predicted_prices, last_ts):
        predicted_data = {}
        for price in predicted_prices:
            last_ts = last_ts + config.INTERVAL*60
            new_data = datetime.datetime.fromtimestamp(last_ts)
            predicted_data[new_data.strftime("%Y-%m-%d %H:%M:%S")] = {'open':price}
        return predicted_data

    def run(self):
        while True:
            for ticker in self.tickers:
                self.logger.debug("Predicting %s" % ticker)
                for algorithm in self.algorithms:
                    while True:
                        last_predicted = self.database.get_last_prediction(ticker,
                                                                           algorithm.name,
                                                                           config.PREDICT_SIZE)
                        if not last_predicted or not last_predicted['hits']['total']:
                            last_first_date = datetime.datetime.strptime("2018-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
                            last_first_ts = float(time.mktime(last_first_date.timetuple()))
                            train_data = self.database.get_market_data(ticker,
                                                                         last_first_ts,
                                                                         config.TRAIN_SIZE)
                            if not train_data or len(train_data['hits']['hits']) != config.TRAIN_SIZE:
                                self.logger.debug("No enough data. Finished Predicting %s" % ticker)
                                break
                            last_ts = train_data['hits']['hits'][-1]['_source']['timestamp']
                            train_data = train_data['hits']['hits']
                            #predict here
                            self.logger.debug("Predicting %s - %s" % (datetime.datetime.fromtimestamp(last_first_ts),
                                                                      datetime.datetime.fromtimestamp(last_ts)))
                            predicted_prices = self.predict(algorithm, train_data)
                            predicted_data = self.generate_predicted_data(predicted_prices, last_ts)
                            self.database.save_predicted_market_data(ticker,algorithm.name,predicted_data)

                        else:
                            last_first_ts = last_predicted['hits']['hits'][-1]['_source']['timestamp']
                            new_train_data = self.database.get_market_data(ticker,
                                                                             last_first_ts,
                                                                             config.PREDICT_SIZE)

                            if not new_train_data or len(new_train_data['hits']['hits']) != config.PREDICT_SIZE:
                                self.logger.debug("No new data. Finished Predicting %s" % ticker)
                                break

                            old_train_data = self.database.get_market_data(ticker,
                                                                             last_first_ts,
                                                                             config.TRAIN_SIZE - config.PREDICT_SIZE,
                                                                             gt=False)
                            last_ts = new_train_data['hits']['hits'][-1]['_source']['timestamp']
                            train_data = old_train_data['hits']['hits'] + new_train_data['hits']['hits']
                            #predict here
                            self.logger.debug("Predicting %s - %s" % (datetime.datetime.fromtimestamp(last_first_ts),
                                                                      datetime.datetime.fromtimestamp(last_ts)))
                            predicted_prices = self.predict(algorithm, train_data)
                            predicted_data = self.generate_predicted_data(predicted_prices, last_ts)
                            self.database.save_predicted_market_data(ticker,algorithm.name,predicted_data)


            self.logger.debug("Sleeping 10 sec..")
            time.sleep(10)

