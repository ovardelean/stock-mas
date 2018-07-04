import requests, json, os

class Alphavantage(object):
    def __init__(self):
        self.API_KEY = 'JLNPXIJCF73NDRWC'

    def import_intraday(self, ticker, interval):
        """
        :param ticker: stock symbol
        :param interval: 1m, 15m, 30m, 60m
        :return: {date: {'open':<>, 'close':<>, 'high':<>, 'low':<>, 'volume':<>}} or None
        """
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol='+ticker+'&interval='+str(interval)+'min&apikey='+self.API_KEY+'&outputsize=full&datatype=json'
        fp = requests.get(url)
        mybytes = fp.text
        stock_data = mybytes.decode("utf8")
        fp.close()

        try:
            json_data = json.loads(stock_data)
            chosen = None
            for key in json_data:
                if 'Time Series' in key:
                    chosen = json_data[key]
            if not chosen:
                return None
            return self.normalize(chosen)
        except Exception as e:
            return None

    def import_daily(self, ticker):
        """
        :param ticker: stock symbol
        :return: {date: {open:<>, 'close':<>, 'high':<>, 'low':<>, 'volume':<>}} or None
        """
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol='+ticker+'&apikey='+self.API_KEY+'&outputsize=full&datatype=json'
        fp = requests.get(url)
        mybytes = fp.text
        stock_data = mybytes.decode("utf8")
        fp.close()

        try:
            json_data = json.loads(stock_data)
            chosen = None
            for key in json_data:
                if 'Time Series' in key:
                    chosen = json_data[key]
            if not chosen:
                return None
            return self.normalize(chosen)
        except Exception as e:
            return None

    def normalize(self, data):
        new_dict = {}
        for date in data:
            if len(date.split()) == 1:
                date = date + " 00:00:00"
            new_dict[date] = {'open':0, 'close':0, 'high':0, 'low':0, 'volume':0}
            for old_key in data[date]:
                for new_key in new_dict[date]:
                    if new_key in old_key.lower():
                        new_dict[date][new_key] = data[date][old_key]
        return new_dict