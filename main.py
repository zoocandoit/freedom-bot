import logging
import time
from binance.client import Client
from data_collection import get_historical_data
from trading_logic import generate_advanced_signals
from trading_execution import place_order
from telegram_alert import send_telegram_message
from config import API_KEY, API_SECRET, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from config import SYMBOL, ASSET, INTERVALS, SHORT_WINDOW, LONG_WINDOW, SIGNAL_WINDOW, PERCENTAGE, LONG_LEVERAGE, SHORT_LEVERAGE
from config import STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE

# 로깅 설정
logging.basicConfig(filename='freedom-bot.log', level=logging.INFO, format='%(asctime)s %(message)s')

# 현재 포지션 상태를 추적하기 위한 변수
current_position = None

def get_asset_balance(client, asset):
    try:
        balance = client.futures_account_balance()
        for item in balance:
            if item['asset'] == asset:
                return float(item['balance'])
        return None
    except Exception as e:
        logging.error(f"Error getting asset balance: {e}")
        send_telegram_message(f"Error getting asset balance: {e}")
        return None

def calculate_quantity(balance, percentage, price, leverage):
    return (balance * percentage * leverage) / price

def set_leverage(client, symbol, leverage):
    try:
        client.futures_change_leverage(symbol=symbol, leverage=leverage)
    except Exception as e:
        logging.error(f"Error setting leverage: {e}")
        send_telegram_message(f"Error setting leverage: {e}")

def main():
    global current_position
    client = Client(API_KEY, API_SECRET)
    
    buy_signal_count = 0
    sell_signal_count = 0
    
    while True:
        try:
            signals = []
            min_length = None
            for interval in INTERVALS:
                data = get_historical_data(client, SYMBOL, interval, "30 minutes ago UTC")
                closing_prices = [float(kline[4]) for kline in data]
                signal = generate_advanced_signals(closing_prices, SHORT_WINDOW, LONG_WINDOW, SIGNAL_WINDOW)
                signals.append(signal)
                if min_length is None or len(signal) < min_length:
                    min_length = len(signal)

            # 모든 신호의 길이를 최소 길이에 맞추기
            signals = [signal[-min_length:] for signal in signals]
            combined_signals = []
            for i in range(min_length):
                interval_signals = [signal[i] for signal in signals]
                if interval_signals.count('BUY') > interval_signals.count('SELL'):
                    combined_signals.append('BUY')
                elif interval_signals.count('SELL') > interval_signals.count('BUY'):
                    combined_signals.append('SELL')
                else:
                    combined_signals.append('HOLD')
            
            current_price = closing_prices[-1]
            balance = get_asset_balance(client, ASSET)
            if balance is None:
                logging.error("Failed to get balance, skipping this iteration.")
                send_telegram_message("Failed to get balance, skipping this iteration.")
                time.sleep(60)
                continue

            logging.info(f"Current combined signal: {combined_signals[-1]}, Price: {current_price}, Balance: {balance}")

            if combined_signals[-1] == 'BUY' and current_position != 'LONG':
                if current_position == 'SHORT':
                    set_leverage(client, SYMBOL, SHORT_LEVERAGE)
                    quantity = calculate_quantity(balance, PERCENTAGE, current_price, SHORT_LEVERAGE)
                    place_order(client, SYMBOL, 'BUY', quantity, current_price, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE, 'SHORT')  # 기존 숏 포지션 종료
                    logging.info(f"CLOSE SHORT position for {quantity} {SYMBOL} at {current_price}")
                    send_telegram_message(f"CLOSE SHORT position for {quantity} {SYMBOL} at {current_price}")

                set_leverage(client, SYMBOL, LONG_LEVERAGE)
                quantity = calculate_quantity(balance, PERCENTAGE, current_price, LONG_LEVERAGE)
                place_order(client, SYMBOL, 'BUY', quantity, current_price, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE, 'LONG')
                logging.info(f"BUY order placed for {quantity} {SYMBOL} at {current_price} for LONG position")
                send_telegram_message(f"BUY order placed for {quantity} {SYMBOL} at {current_price} for LONG position")
                current_position = 'LONG'
            elif combined_signals[-1] == 'SELL' and current_position != 'SHORT':
                if current_position == 'LONG':
                    set_leverage(client, SYMBOL, LONG_LEVERAGE)
                    quantity = calculate_quantity(balance, PERCENTAGE, current_price, LONG_LEVERAGE)
                    place_order(client, SYMBOL, 'SELL', quantity, current_price, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE, 'LONG')  # 기존 롱 포지션 종료
                    logging.info(f"CLOSE LONG position for {quantity} {SYMBOL} at {current_price}")
                    send_telegram_message(f"CLOSE LONG position for {quantity} {SYMBOL} at {current_price}")

                set_leverage(client, SYMBOL, SHORT_LEVERAGE)
                quantity = calculate_quantity(balance, PERCENTAGE, current_price, SHORT_LEVERAGE)
                place_order(client, SYMBOL, 'SELL', quantity, current_price, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE, 'SHORT')
                logging.info(f"SELL order placed for {quantity} {SYMBOL} at {current_price} for SHORT position")
                send_telegram_message(f"SELL order placed for {quantity} {SYMBOL} at {current_price} for SHORT position")
                current_position = 'SHORT'
        
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            send_telegram_message(f"An error occurred: {e}")
        
        time.sleep(900)  # 15분 대기

if __name__ == "__main__":
    main()
