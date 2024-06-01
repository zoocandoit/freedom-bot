import numpy as np

def simple_moving_average(data, window):
    return np.convolve(data, np.ones(window), 'valid') / window

def exponential_moving_average(data, window):
    ema = [sum(data[:window]) / window]
    multiplier = 2 / (window + 1)
    for price in data[window:]:
        ema.append((price - ema[-1]) * multiplier + ema[-1])
    return ema

def generate_signals(data, short_window, long_window):
    signals = []
    short_sma = simple_moving_average(data, short_window)
    long_sma = simple_moving_average(data, long_window)
    
    for i in range(len(long_sma)):
        if short_sma[i] > long_sma[i]:
            signals.append('BUY')
        else:
            signals.append('SELL')
    
    return signals

def generate_advanced_signals(data, short_window, long_window):
    signals = []
    short_ema = exponential_moving_average(data, short_window)
    long_ema = exponential_moving_average(data, long_window)
    rsi = relative_strength_index(data, window=14)

    for i in range(len(long_ema)):
        if short_ema[i] > long_ema[i] and rsi[i] < 70:
            signals.append('BUY')
        elif short_ema[i] < long_ema[i] and rsi[i] > 30:
            signals.append('SELL')
        else:
            signals.append('HOLD')

    return signals

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
