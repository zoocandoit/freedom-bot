import numpy as np

def simple_moving_average(data, window):
    return np.convolve(data, np.ones(window), 'valid') / window

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
