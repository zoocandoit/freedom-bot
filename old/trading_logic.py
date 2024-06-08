import numpy as np

def simple_moving_average(data, window):
    return np.convolve(data, np.ones(window), 'valid') / window

def exponential_moving_average(data, window):
    ema = [sum(data[:window]) / window]
    multiplier = 2 / (window + 1)
    for price in data[window:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

def relative_strength_index(data, window=14):
    deltas = np.diff(data)
    seed = deltas[:window+1]
    up = seed[seed >= 0].sum() / window
    down = -seed[seed < 0].sum() / window
    rs = up / down
    rsi = np.zeros_like(data)
    rsi[:window] = 100. - 100. / (1. + rs)

    for i in range(window, len(data)):
        delta = deltas[i - 1]  # cause the diff is 1 shorter

        if delta > 0:
            upval = delta
            downval = 0.
        else:
            upval = 0.
            downval = -delta

        up = (up * (window - 1) + upval) / window
        down = (down * (window - 1) + downval) / window

        rs = up / down
        rsi[i] = 100. - 100. / (1. + rs)

    return rsi

def macd(data, short_window=12, long_window=26, signal_window=9):
    short_ema = exponential_moving_average(data, short_window)
    long_ema = exponential_moving_average(data, long_window)
    macd_line = np.array(short_ema[len(short_ema)-len(long_ema):]) - np.array(long_ema)
    signal_line = exponential_moving_average(macd_line, signal_window)
    return macd_line[len(macd_line)-len(signal_line):], signal_line

def generate_advanced_signals(data, short_window, long_window, signal_window):
    signals = []
    short_ema = exponential_moving_average(data, short_window)
    long_ema = exponential_moving_average(data, long_window)
    rsi = relative_strength_index(data, window=14)
    macd_line, signal_line = macd(data, short_window=short_window, long_window=long_window, signal_window=signal_window)

    for i in range(len(long_ema)):
        if short_ema[i] > long_ema[i] and rsi[i] < 70 and macd_line[i] > signal_line[i]:
            signals.append('BUY')
        elif short_ema[i] < long_ema[i] and rsi[i] > 30 and macd_line[i] < signal_line[i]:
            signals.append('SELL')
        else:
            signals.append('HOLD')

    return signals
