#stock-mas

Project Description:

    This project introduces a method of implementing agents for stock prediction. Three categories of agents are introduced here. Feeder, Predictor and Evaluator. Each of them has a different purpose and interacts with one another through elasticsearch.
    The database environment used is Elasticsearch. A search-engine database that allows storage and queries through no-SQL data.
    The visualization of data is done through Kibana, it works on top of Elasticsearch and provides visual graphics of real-time data.

Agents description:

    Feeder

    Tries to feed market data from multiple sources. One example of source is “alphavantage”, an open platform and database of market data that exposes an API for fetching data. The agent is responsible for feeding the environment with market data from outside of the system.

    Predictor

    This agent tries to predict data based on previous market prices. It has two algorithms implemented, a Support Vector Machine Regression (SVR) and a Random pick (RAND). It is configurable to add more prediction algorithms.

    Evaluator

    This agent will try to evaluate the performance of Predictor agent. It will try to fetch new data from Feeder and new predictions from Predictor.
    It will compute an absolute difference of actual price and predicted price for every prediction algorithm and every ticker available in the environment. Besides it will also provide a market direction and a prediction direction for previous data by subtracting now-data from previous-data, a <0 value is a downfall and a >0 value is an uprise.
