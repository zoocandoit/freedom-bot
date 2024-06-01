import logging
import time
from binance.client import Client
from data_collection import get_historical_data
from trading_logic import generate_advanced_signals
from trading_execution import place_order
from telegram_alert import send_telegram_message

# 로깅 설정
logging.basicConfig(filename='freedom-bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

def get_asset_balance(client, asset):
    try:
        balance = client.get_asset_balance(asset)
        return float(balance['free'])
    except Exception as e:
        logging.error(f"Error getting asset balance: {e}")
        send_telegram_message(f"Error getting asset balance: {e}")
        return None

def calculate_quantity(balance, percentage, price):
    return (balance * percentage) / price

def fibonacci_sequence(n):
    fib_sequence = [0, 1]
    for i in range(2, n):
        fib_sequence.append(fib_sequence[-1] + fib_sequence[-2])
    return fib_sequence

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
    fibonacci_levels = fibonacci_sequence(10)  # 피보나치 수열의 초기 10개 값
    stop_loss_percentage = fibonacci_levels[3] / 100  # 피보나치 수열의 4번째 값 (2%)
    take_profit_percentage = fibonacci_levels[5] / 100  # 피보나치 수열의 6번째 값 (5%)
    signal_threshold = 3  # 신호 발생 횟수 임계값

    buy_signal_count = 0
    sell_signal_count = 0
    
    while True:
        try:
            data = get_historical_data(client, symbol, interval, "30 minutes ago UTC")
            closing_prices = [float(kline[4]) for kline in data]
            signals = generate_advanced_signals(closing_prices, short_window, long_window)
            
            current_price = closing_prices[-1]
            balance = get_asset_balance(client, asset)
            if balance is None:
                logging.error("Failed to get balance, skipping this iteration.")
                send_telegram_message("Failed to get balance, skipping this iteration.")
                time.sleep(60)
                continue

            quantity = calculate_quantity(balance, percentage, current_price)
            
            if signals[-1] == 'BUY':
                buy_signal_count += 1
                sell_signal_count = 0  # 매수 신호가 발생하면 매도 신호 카운트는 초기화
            elif signals[-1] == 'SELL':
                sell_signal_count += 1
                buy_signal_count = 0  # 매도 신호가 발생하면 매수 신호 카운트는 초기화
            else:
                buy_signal_count = 0
                sell_signal_count = 0
            
            if buy_signal_count >= signal_threshold:
                place_order(client, symbol, 'BUY', quantity, current_price, stop_loss_percentage, take_profit_percentage)
                logging.info(f"BUY order placed for {quantity} {symbol} at {current_price}")
                send_telegram_message(f"BUY order placed for {quantity} {symbol} at {current_price}")
                buy_signal_count = 0  # 거래 후 신호 카운트 초기화
            elif sell_signal_count >= signal_threshold:
                place_order(client, symbol, 'SELL', quantity, current_price, stop_loss_percentage, take_profit_percentage)
                logging.info(f"SELL order placed for {quantity} {symbol} at {current_price}")
                send_telegram_message(f"SELL order placed for {quantity} {symbol} at {current_price}")
                sell_signal_count = 0  # 거래 후 신호 카운트 초기화
        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            send_telegram_message(f"An error occurred: {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
