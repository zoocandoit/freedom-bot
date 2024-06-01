import logging
import time
from binance.client import Client
from data_collection import get_historical_data
from trading_logic import generate_advanced_signals
from trading_execution import place_order
from telegram_alert import send_telegram_message
from config import API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from config import SYMBOL, ASSET, INTERVAL, SHORT_WINDOW, LONG_WINDOW, PERCENTAGE, SIGNAL_THRESHOLD
from config import STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE

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

def main():
    client = Client(API_KEY, API_SECRET)

    buy_signal_count = 0
    sell_signal_count = 0
    
    while True:
        try:
            data = get_historical_data(client, SYMBOL, INTERVAL, "30 minutes ago UTC")
            closing_prices = [float(kline[4]) for kline in data]
            signals = generate_advanced_signals(closing_prices, SHORT_WINDOW, LONG_WINDOW)
            
            current_price = closing_prices[-1]
            balance = get_asset_balance(client, ASSET)
            if balance is None:
                logging.error("Failed to get balance, skipping this iteration.")
                send_telegram_message("Failed to get balance, skipping this iteration.")
                time.sleep(60)
                continue

            quantity = calculate_quantity(balance, PERCENTAGE, current_price)
            
            if signals[-1] == 'BUY':
                buy_signal_count += 1
                sell_signal_count = 0  # 매수 신호가 발생하면 매도 신호 카운트는 초기화
            elif signals[-1] == 'SELL':
                sell_signal_count += 1
                buy_signal_count = 0  # 매도 신호가 발생하면 매수 신호 카운트는 초기화
            else:
                buy_signal_count = 0
                sell_signal_count = 0
            
            if buy_signal_count >= SIGNAL_THRESHOLD:
                place_order(client, SYMBOL, 'BUY', quantity, current_price, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE)
                logging.info(f"BUY order placed for {quantity} {SYMBOL} at {current_price}")
                send_telegram_message(f"BUY order placed for {quantity} {SYMBOL} at {current_price}")
                buy_signal_count = 0  # 거래 후 신호 카운트 초기화
            elif sell_signal_count >= SIGNAL_THRESHOLD:
                place_order(client, SYMBOL, 'SELL', quantity, current_price, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE)
                logging.info(f"SELL order placed for {quantity} {SYMBOL} at {current_price}")
                send_telegram_message(f"SELL order placed for {quantity} {SYMBOL} at {current_price}")
                sell_signal_count = 0  # 거래 후 신호 카운트 초기화
        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            send_telegram_message(f"An error occurred: {e}")
        
        time.sleep(60)

if __name__ == "__main__":
    main()
