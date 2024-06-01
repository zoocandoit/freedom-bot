import time
from binance.client import Client
from data_collection import get_historical_data
from trading_logic import generate_signals
from trading_execution import place_order

def main():
    api_key = 'YOUR_API_KEY'
    api_secret = 'YOUR_API_SECRET'
    client = Client(api_key, api_secret)

    symbol = 'BTCUSDT'
    interval = client.KLINE_INTERVAL_1HOUR
    short_window = 5
    long_window = 20
    quantity = 0.001
    
    while True:
        data = get_historical_data(client, symbol, interval, "1 day ago UTC")
        closing_prices = [float(kline[4]) for kline in data]
        signals = generate_signals(closing_prices, short_window, long_window)
        
        if signals[-1] == 'BUY':
            place_order(client, symbol, 'BUY', quantity)
        elif signals[-1] == 'SELL':
            place_order(client, symbol, 'SELL', quantity)
        
        time.sleep(3600)  # 1시간 대기

if __name__ == "__main__":
    main()
