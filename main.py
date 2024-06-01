import time
from binance.client import Client
from data_collection import get_historical_data
from trading_logic import generate_advanced_signals
from trading_execution import place_order

def get_asset_balance(client, asset):
    balance = client.get_asset_balance(asset)
    return float(balance['free'])

def calculate_quantity(balance, percentage, price):
    return (balance * percentage) / price

def main():
    api_key = 'YOUR_API_KEY'
    api_secret = 'YOUR_API_SECRET'
    client = Client(api_key, api_secret)

    symbol = 'BTCUSDT'
    asset = 'USDT'
    interval = client.KLINE_INTERVAL_1MINUTE
    short_window = 3
    long_window = 7
    percentage = 0.01
    stop_loss_percentage = 0.01  # 손절매 설정 (1%)
    take_profit_percentage = 0.02  # 이익 실현 설정 (2%)
    
    while True:
        data = get_historical_data(client, symbol, interval, "30 minutes ago UTC")
        closing_prices = [float(kline[4]) for kline in data]
        signals = generate_advanced_signals(closing_prices, short_window, long_window)
        
        current_price = closing_prices[-1]
        balance = get_asset_balance(client, asset)
        quantity = calculate_quantity(balance, percentage, current_price)
        
        if signals[-1] == 'BUY':
            place_order(client, symbol, 'BUY', quantity, current_price, stop_loss_percentage, take_profit_percentage)
        elif signals[-1] == 'SELL':
            place_order(client, symbol, 'SELL', quantity, current_price, stop_loss_percentage, take_profit_percentage)
        
        time.sleep(60)

if __name__ == "__main__":
    main()