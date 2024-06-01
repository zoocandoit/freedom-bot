from binance.client import Client

api_key = 'YOUR_API_KEY'
api_secret = 'YOUR_API_SECRET'

client = Client(api_key, api_secret)

def get_historical_data(symbol, interval, start_str):
    return client.get_historical_klines(symbol, interval, start_str)
