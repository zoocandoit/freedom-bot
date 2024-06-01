from binance.client import Client

def get_historical_data(client, symbol, interval, start_str):
    try:
        klines = client.get_historical_klines(symbol, interval, start_str)
        data = []
        for kline in klines:
            data.append({
                'open_time': kline[0],
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
        return data
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def get_multiple_symbols_data(client, symbols, interval, start_str):
    data = {}
    for symbol in symbols:
        data[symbol] = get_historical_data(client, symbol, interval, start_str)
    return data
