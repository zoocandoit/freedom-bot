from binance.client import Client

def get_historical_data(client, symbol, interval, start_str):
    return client.get_historical_klines(symbol, interval, start_str)

