import logging
import pandas as pd
from binance.client import Client
from data_collection import get_historical_data
from trading_logic import generate_advanced_signals
from config import API_KEY, API_SECRET, SYMBOL, ASSET, INTERVALS, SHORT_WINDOW, LONG_WINDOW, PERCENTAGE, SIGNAL_THRESHOLD, LONG_LEVERAGE, SHORT_LEVERAGE, STOP_LOSS_PERCENTAGE, TAKE_PROFIT_PERCENTAGE

# 로깅 설정
logging.basicConfig(filename='freedom-bot-backtest.log', level=logging.INFO, format='%(asctime)s %(message)s')

# 현재 포지션 상태를 추적하기 위한 변수
current_position = None

def calculate_quantity(balance, percentage, price, leverage):
    return (balance * percentage * leverage) / price

def backtest(data, short_window, long_window, initial_balance=10000, percentage=PERCENTAGE, signal_threshold=SIGNAL_THRESHOLD, long_leverage=LONG_LEVERAGE, short_leverage=SHORT_LEVERAGE):
    global current_position
    signals = generate_advanced_signals(data['close'].values, short_window, long_window)
    balance = initial_balance
    position_quantity = 0
    position_entry_price = 0

    buy_signal_count = 0
    sell_signal_count = 0

    print("Initial balance:", balance)

    for i in range(len(signals)):
        current_price = data['close'].values[i]

        if signals[i] == 'BUY':
            buy_signal_count += 1
            sell_signal_count = 0
        elif signals[i] == 'SELL':
            sell_signal_count += 1
            buy_signal_count = 0
        else:
            buy_signal_count = 0
            sell_signal_count = 0

        if buy_signal_count >= signal_threshold and current_position != 'LONG':
            if current_position == 'SHORT':
                position_quantity = (balance * percentage * short_leverage) / current_price
                balance += position_quantity * (position_entry_price - current_price)
                print(f"Closed SHORT at {current_price}, balance: {balance}")
                logging.info(f"Closed SHORT at {current_price}, balance: {balance}")
                position_quantity = 0

            position_quantity = (balance * percentage * long_leverage) / current_price
            balance -= position_quantity * current_price / long_leverage
            current_position = 'LONG'
            position_entry_price = current_price
            buy_signal_count = 0
            print(f"Opened LONG at {current_price}, balance: {balance}, position_quantity: {position_quantity}")
            logging.info(f"Opened LONG at {current_price}, balance: {balance}, position_quantity: {position_quantity}")

        elif sell_signal_count >= signal_threshold and current_position != 'SHORT':
            if current_position == 'LONG':
                position_quantity = (balance * percentage * long_leverage) / current_price
                balance += position_quantity * (current_price - position_entry_price)
                print(f"Closed LONG at {current_price}, balance: {balance}")
                logging.info(f"Closed LONG at {current_price}, balance: {balance}")
                position_quantity = 0

            position_quantity = (balance * percentage * short_leverage) / current_price
            balance -= position_quantity * current_price / short_leverage
            current_position = 'SHORT'
            position_entry_price = current_price
            sell_signal_count = 0
            print(f"Opened SHORT at {current_price}, balance: {balance}, position_quantity: {position_quantity}")
            logging.info(f"Opened SHORT at {current_price}, balance: {balance}, position_quantity: {position_quantity}")

    # 마지막 남은 포지션 청산
    if current_position == 'LONG':
        balance += position_quantity * data['close'].values[-1]
        print(f"Closed LONG at end, balance: {balance}")
        logging.info(f"Closed LONG at end, balance: {balance}")
    elif current_position == 'SHORT':
        balance += position_quantity * (position_entry_price - data['close'].values[-1])
        print(f"Closed SHORT at end, balance: {balance}")
        logging.info(f"Closed SHORT at end, balance: {balance}")

    return balance

if __name__ == "__main__":
    client = Client(API_KEY, API_SECRET)
    # 데이터 수집 기간을 1개월로 설정
    data = {}
    for interval in INTERVALS:
        data[interval] = get_historical_data(client, SYMBOL, interval, "10 Apr, 2024", "11 Apr, 2024")
    
    if all(data.values()):
        print(data[INTERVALS[0]].head())  # 데이터 확인
        combined_signals = []
        for i in range(len(data[INTERVALS[0]]['close'].values)):
            interval_signals = []
            for interval in INTERVALS:
                interval_signals.append(generate_advanced_signals(data[interval]['close'].values, SHORT_WINDOW, LONG_WINDOW)[i])
            if interval_signals.count('BUY') > interval_signals.count('SELL'):
                combined_signals.append('BUY')
            elif interval_signals.count('SELL') > interval_signals.count('BUY'):
                combined_signals.append('SELL')
            else:
                combined_signals.append('HOLD')
        
        final_balance = backtest(pd.DataFrame({'close': data[INTERVALS[0]]['close'].values, 'signal': combined_signals}), short_window=SHORT_WINDOW, long_window=LONG_WINDOW, initial_balance=10000, percentage=PERCENTAGE, signal_threshold=SIGNAL_THRESHOLD, long_leverage=LONG_LEVERAGE, short_leverage=SHORT_LEVERAGE)
        print(f"Final balance: {final_balance}")
    else:
        print("Failed to retrieve historical data")
