import os, sys
import datetime, time
import elasticsearch

sys.path.append("..")
import config

class EsDatabase(object):
    def __init__(self):
        self.es = elasticsearch.Elasticsearch(hosts=['localhost'])
        self.es_indices = elasticsearch.client.IndicesClient(self.es)
        self.check_indexes()

    def check_indexes(self):
        if not self.es_indices.exists(index=config.INDEX_MARKET):
            self.es_indices.create(index=config.INDEX_MARKET)
        if not self.es_indices.exists(index=config.INDEX_MARKET_PREDICTION):
            self.es_indices.create(index=config.INDEX_MARKET_PREDICTION)
        if not self.es_indices.exists(index=config.INDEX_MARKET_EVALUATION):
            self.es_indices.create(index=config.INDEX_MARKET_EVALUATION)

    def save_market_data(self, ticker, data):
        for date_info in data:
            date_time = datetime.datetime.strptime(date_info, '%Y-%m-%d %H:%M:%S')
            timestamp = time.mktime(date_time.timetuple())
            _id = "%s-%d" % (ticker, timestamp)

            if not self.es.exists(index=config.INDEX_MARKET, doc_type='doc', id=_id):
                body = {'date': date_time,
                        'timestamp': timestamp,
                        'ticker': ticker,
                        'market_data': {k:float(data[date_info][k]) for k in data[date_info]}}
                self.es.create(index=config.INDEX_MARKET, doc_type='doc', id=_id, body=body, refresh=True)

    def save_predicted_market_data(self, ticker, alg, data):
        level_counter = 1
        for date_info in data:
            date_time = datetime.datetime.strptime(date_info, '%Y-%m-%d %H:%M:%S')
            timestamp = time.mktime(date_time.timetuple())
            _id = "%s-%s-%s" % (ticker, alg, timestamp)
            if not self.es.exists(index=config.INDEX_MARKET_PREDICTION, doc_type='doc', id=_id):
                body = {'date': date_time,
                        'timestamp': timestamp,
                        'ticker': ticker,
                        'algorithm': alg,
                        'prediction_level': level_counter,
                        '%s_prediction'%alg: {k: float(data[date_info][k]) for k in data[date_info]}}
                self.es.create(index=config.INDEX_MARKET_PREDICTION, doc_type='doc', id=_id, body=body, refresh=True)
                level_counter += 1

    def save_evaluation(self, ticker, algorithm, data):
        for date_info in data:
            date_time = datetime.datetime.strptime(date_info, '%Y-%m-%d %H:%M:%S')
            timestamp = time.mktime(date_time.timetuple())
            _id = "EVAL-%s-%s-%s" % (ticker, algorithm, timestamp)
            if not self.es.exists(index=config.INDEX_MARKET_EVALUATION, doc_type='doc', id=_id):
                body = {'date': date_time,
                        'timestamp': timestamp,
                        'ticker': ticker,
                        'algorithm': algorithm,
                        'market_data_evaluation': data[date_info]}
                self.es.create(index=config.INDEX_MARKET_EVALUATION, doc_type='doc', id=_id, body=body, refresh=True)

    def get_last_prediction(self, ticker, alg, size):
        query={
            'query':{"bool":{
                "must":[{"match":{"algorithm":alg}},
                         {"match":{"ticker": ticker}}]
            }},
            "sort":{"date":{"order":"desc"}},
            "size":size
        }
        try:
            return self.es.search(index=config.INDEX_MARKET_PREDICTION, doc_type='doc', body=query)
        except Exception as e:
            print e
            return None

    def get_market_data(self, ticker, timestamp, size, gt=True):
        ts_direction = "gte"
        order = "asc"
        if not gt:
            ts_direction = "lt"
            order = "desc"
        query={
            'query':{"bool":{
                "must":[{"match":{"ticker": ticker}},
                        {"range":{"timestamp":{ts_direction:timestamp}}}]
            }},
            "sort":{"date":{"order":order}},
            "size":size
        }
        try:
            return self.es.search(index=config.INDEX_MARKET, doc_type='doc', body=query)
        except Exception as e:
            print e
            return None

    def get_last_evaluated(self, ticker, alg):
        query={
            'query':{"bool":{
                "must":[{"match":{"ticker": ticker}},
                        {"match": {"algorithm": alg}}]
            }},
            "sort":{"date":{"order":"desc"}},
            "size":1
        }
        try:
            return self.es.search(index=config.INDEX_MARKET_EVALUATION, doc_type='doc', body=query)
        except Exception as e:
            print e

    def get_prediction_data(self, ticker, algorithm, timestamp, size, gt=True):
        ts_direction = "gte"
        order = "asc"
        if not gt:
            ts_direction = "lt"
            order = "desc"
        query={
            'query':{"bool":{
                "must":[{"match":{"ticker": ticker}},
                        {"match": {"algorithm": algorithm}},
                        {"range":{"timestamp":{ts_direction:timestamp}}}]
            }},
            "sort":{"date":{"order":order}},
            "size":size
        }
        try:
            return self.es.search(index=config.INDEX_MARKET_PREDICTION, doc_type='doc', body=query)
        except Exception as e:
            print e
            return None


if __name__ == "__main__":
    sys.path.append("..")
    import pprint
    es = EsDatabase()
    #x = es.get_training_data("AAPL", datetime.datetime.strptime("2018-06-19 00:00:00", '%Y-%m-%d %H:%M:%S'), 10)
    #pprint.pprint(x)
    #print es.get_last_prediction("AAPL", "SVM")