import time
import logging

import config

from agents.feeder.alphavantage import Alphavantage
from database.elasticsearch_db import EsDatabase
from utils.logger import create_logger


class Feeder(object):
    def __init__(self):
        self.database = EsDatabase()
        self.alphavantage = Alphavantage()
        self.tickers = config.TICKERS
        self.interval = config.INTERVAL
        self.logger = create_logger('Feeder')
        pass

    def run(self):
        while True:
            for ticker in self.tickers:
                try:
                    market_data = self.alphavantage.import_intraday(ticker, self.interval)
                #market_data = self.alphavantage.import_daily(ticker)
                except Exception as e:
                    self.logger.error(e)
                    market_data = None
                if not market_data:
                    self.logger.debug("No market data for %s" % ticker)
                else:
                    self.database.save_market_data(ticker, market_data)
                    self.logger.debug("Saved for %s" % ticker)
            self.logger.debug("Sleeping 60 sec..")
            time.sleep(60)

