import time
from data_collection import get_historical_data
from trading_logic import generate_signals
from trade_execution import place_order

def main():
    symbol = 'BTCUSDT'
    interval = Client.KLINE_INTERVAL_1HOUR
    short_window = 5
    long_window = 20
    quantity = 0.001
    
    while True:
        data = get_historical_data(symbol, interval, "1 day ago UTC")
        closing_prices = [float(kline[4]) for kline in data]
        signals = generate_signals(closing_prices, short_window, long_window)
        
        if signals[-1] == 'BUY':
            place_order(symbol, 'BUY', quantity)
        elif signals[-1] == 'SELL':
            place_order(symbol, 'SELL', quantity)
        
        time.sleep(3600)  # 1시간 대기

if __name__ == "__main__":
    main()
