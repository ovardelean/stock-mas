import time, datetime

import config

from database.elasticsearch_db import EsDatabase
from utils.logger import create_logger


class Evaluator(object):
    def __init__(self):
        self.database = EsDatabase()
        self.tickers = config.TICKERS
        self.logger = create_logger('Evaluater')
        pass

    def evaluate_data(self, alg, market_batch, predict_batch):
        evaluated_data = {}
        i, j = 1, 1
        while i < len(market_batch) and j < len(predict_batch):
            if market_batch[i]['_source']['timestamp'] < predict_batch[j]['_source']['timestamp']:
                i += 1
                continue
            elif market_batch[i]['_source']['timestamp'] > predict_batch[j]['_source']['timestamp']:
                j += 1
                continue
            else:
                date_time = datetime.datetime.fromtimestamp(market_batch[i]['_source']['timestamp'])
                evaluated_data[date_time.strftime("%Y-%m-%d %H:%M:%S")] = {
                        'abs': abs(market_batch[i]['_source']['market_data']['open'] -
                                   predict_batch[j]['_source']['%s_prediction'%alg]['open']),
                        'market_direction': market_batch[i]['_source']['market_data']['open'] -
                                            market_batch[i-1]['_source']['market_data']['open'],
                        'prediction_direction': predict_batch[j]['_source']['%s_prediction'%alg]['open'] -
                                                predict_batch[j-1]['_source']['%s_prediction'%alg]['open'],
                    }
                i += 1
                j += 1
        return evaluated_data

    def run(self):
        while True:
            for ticker in config.TICKERS:
                self.logger.debug("Evaluating %s" % ticker)
                for algorithm in config.ALGORITHMS:
                    initial_ts = 0
                    while True:
                        if not initial_ts:
                            last_evaluated = self.database.get_last_evaluated(ticker, algorithm)
                            if not last_evaluated or not last_evaluated['hits']['total']:
                                initial_ts = datetime.datetime.strptime("2018-01-01 00:00:00", '%Y-%m-%d %H:%M:%S')
                                initial_ts = float(time.mktime(initial_ts.timetuple()))
                            else:
                                initial_ts = last_evaluated['hits']['hits'][0]['_source']['timestamp']

                        market_batch = self.database.get_market_data(ticker, initial_ts, config.EVALUATE_BATCH)
                        predict_batch = self.database.get_prediction_data(ticker, algorithm, initial_ts, config.EVALUATE_BATCH)

                        if not market_batch or not predict_batch:
                            self.logger.error("No initial data for %s" % ticker)
                            break

                        if len(market_batch['hits']['hits']) < 2 or len(predict_batch['hits']['hits']) < 2:
                            self.logger.debug("No more data for %s" % ticker)
                            break

                        initial_ts = market_batch['hits']['hits'][-1]['_source']['timestamp']

                        evaluation = self.evaluate_data(algorithm, market_batch['hits']['hits'], predict_batch['hits']['hits'])
                        if not evaluation:
                            self.logger.debug("No evaluation for %s" % datetime.datetime.fromtimestamp(initial_ts))
                            continue

                        #save evaluation
                        self.logger.debug("Evaluated %s" % datetime.datetime.fromtimestamp(initial_ts))
                        self.database.save_evaluation(ticker, algorithm, evaluation)


            self.logger.debug("Sleeping 10 seconds..")
            time.sleep(10)

