from binance.client import Client
import pandas as pd

def get_historical_data(client, symbol, interval, start_str, end_str=None):
    try:
        klines = client.get_historical_klines(symbol, interval, start_str, end_str)
        data = []
        for kline in klines:
            data.append({
                'timestamp': kline[0],
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[5]),
                'close_time': kline[6],
                'quote_asset_volume': float(kline[7]),
                'number_of_trades': kline[8],
                'taker_buy_base_asset_volume': float(kline[9]),
                'taker_buy_quote_asset_volume': float(kline[10])
            })
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        return df
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
