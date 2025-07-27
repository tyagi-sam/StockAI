"""
Custom Technical Indicators Module
Provides precise technical analysis calculations using pandas and numpy.
"""

import numpy as np
import pandas as pd
from typing import Tuple, Optional

def calculate_rsi(prices: np.ndarray, period: int = 14) -> float:
    """
    Calculate Relative Strength Index (RSI) using Wilder's smoothing method
    
    Args:
        prices: Array of closing prices
        period: RSI period (default: 14)
    
    Returns:
        RSI value (0-100)
    """
    if len(prices) < period + 1:
        return 50.0  # Neutral RSI if not enough data
    
    deltas = np.diff(prices)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Use Wilder's smoothing method
    avg_gains = np.mean(gains[:period])
    avg_losses = np.mean(losses[:period])
    
    # Apply Wilder's smoothing for subsequent periods
    for i in range(period, len(gains)):
        avg_gains = (avg_gains * (period - 1) + gains[i]) / period
        avg_losses = (avg_losses * (period - 1) + losses[i]) / period
    
    # Calculate RSI
    if avg_losses == 0:
        return 100.0
    
    rs = avg_gains / avg_losses
    rsi = 100 - (100 / (1 + rs))
    
    return float(rsi)

def calculate_macd(prices: np.ndarray, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[float, float]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    
    Args:
        prices: Array of closing prices
        fast: Fast EMA period (default: 12)
        slow: Slow EMA period (default: 26)
        signal: Signal line period (default: 9)
    
    Returns:
        Tuple of (MACD line, Signal line)
    """
    if len(prices) < slow + signal:
        return 0.0, 0.0
    
    # Calculate EMAs
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    # MACD line
    macd_line = ema_fast - ema_slow
    
    # Signal line (EMA of MACD line)
    macd_values = []
    for i in range(len(prices)):
        if i >= slow - 1:
            ema_fast_val = calculate_ema(prices[:i+1], fast)
            ema_slow_val = calculate_ema(prices[:i+1], slow)
            macd_values.append(ema_fast_val - ema_slow_val)
        else:
            macd_values.append(0)
    
    macd_array = np.array(macd_values)
    signal_line = calculate_ema(macd_array, signal)
    
    return float(macd_line), float(signal_line)

def calculate_ema(prices: np.ndarray, period: int) -> float:
    """
    Calculate Exponential Moving Average (EMA)
    
    Args:
        prices: Array of prices
        period: EMA period
    
    Returns:
        EMA value
    """
    if len(prices) < period:
        return float(np.mean(prices))
    
    # Calculate multiplier
    multiplier = 2 / (period + 1)
    
    # Start with SMA of first 'period' values
    ema = np.mean(prices[:period])
    
    # Calculate EMA using the standard formula
    for i in range(period, len(prices)):
        ema = (prices[i] * multiplier) + (ema * (1 - multiplier))
    
    return float(ema)

def calculate_sma(prices: np.ndarray, period: int) -> float:
    """
    Calculate Simple Moving Average (SMA)
    
    Args:
        prices: Array of prices
        period: SMA period
    
    Returns:
        SMA value
    """
    if len(prices) < period:
        return float(np.mean(prices))
    
    return float(np.mean(prices[-period:]))

def calculate_bollinger_bands(prices: np.ndarray, period: int = 20, std_dev: float = 2.0) -> Tuple[float, float, float]:
    """
    Calculate Bollinger Bands
    
    Args:
        prices: Array of closing prices
        period: Period for SMA (default: 20)
        std_dev: Standard deviation multiplier (default: 2.0)
    
    Returns:
        Tuple of (upper_band, middle_band, lower_band)
    """
    if len(prices) < period:
        middle = float(np.mean(prices))
        return middle, middle, middle
    
    # Calculate SMA for middle band
    middle = calculate_sma(prices, period)
    
    # Calculate standard deviation of the last 'period' values
    recent_prices = prices[-period:]
    std = float(np.std(recent_prices, ddof=0))  # Use population std dev
    
    upper = middle + (std_dev * std)
    lower = middle - (std_dev * std)
    
    return float(upper), float(middle), float(lower)

def calculate_stochastic(high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                        k_period: int = 14, d_period: int = 3) -> Tuple[float, float]:
    """
    Calculate Stochastic Oscillator
    
    Args:
        high: Array of high prices
        low: Array of low prices
        close: Array of closing prices
        k_period: %K period (default: 14)
        d_period: %D period (default: 3)
    
    Returns:
        Tuple of (%K, %D)
    """
    if len(close) < k_period:
        return 50.0, 50.0
    
    # Calculate %K
    lowest_low = np.min(low[-k_period:])
    highest_high = np.max(high[-k_period:])
    
    if highest_high == lowest_low:
        k_percent = 50.0
    else:
        k_percent = ((close[-1] - lowest_low) / (highest_high - lowest_low)) * 100
    
    # Calculate %D (SMA of %K)
    k_values = []
    for i in range(k_period, len(close)):
        period_low = np.min(low[i-k_period:i])
        period_high = np.max(high[i-k_period:i])
        if period_high == period_low:
            k_val = 50.0
        else:
            k_val = ((close[i-1] - period_low) / (period_high - period_low)) * 100
        k_values.append(k_val)
    
    if len(k_values) < d_period:
        d_percent = k_percent
    else:
        d_percent = np.mean(k_values[-d_period:])
    
    return float(k_percent), float(d_percent)

def calculate_atr(high: np.ndarray, low: np.ndarray, close: np.ndarray, period: int = 14) -> float:
    """
    Calculate Average True Range (ATR)
    
    Args:
        high: Array of high prices
        low: Array of low prices
        close: Array of closing prices
        period: ATR period (default: 14)
    
    Returns:
        ATR value
    """
    if len(close) < period + 1:
        return 0.0
    
    # Calculate True Range
    tr_values = []
    for i in range(1, len(close)):
        tr1 = high[i] - low[i]  # Current high - current low
        tr2 = abs(high[i] - close[i-1])  # Current high - previous close
        tr3 = abs(low[i] - close[i-1])   # Current low - previous close
        tr = max(tr1, tr2, tr3)
        tr_values.append(tr)
    
    # Calculate ATR (SMA of True Range)
    atr = np.mean(tr_values[-period:])
    
    return float(atr)

def get_technical_indicators(close_prices: np.ndarray, high_prices: np.ndarray = None, 
                           low_prices: np.ndarray = None) -> dict:
    """
    Calculate all technical indicators for a given price series
    
    Args:
        close_prices: Array of closing prices
        high_prices: Array of high prices (optional)
        low_prices: Array of low prices (optional)
    
    Returns:
        Dictionary containing all technical indicators
    """
    indicators = {}
    
    # Basic indicators that only need closing prices
    indicators['rsi'] = calculate_rsi(close_prices, 14)
    indicators['macd'], indicators['macd_signal'] = calculate_macd(close_prices, 12, 26, 9)
    indicators['sma_20'] = calculate_sma(close_prices, 20)
    indicators['sma_50'] = calculate_sma(close_prices, 50)
    indicators['ema_12'] = calculate_ema(close_prices, 12)
    indicators['ema_26'] = calculate_ema(close_prices, 26)
    
    # Bollinger Bands
    bb_upper, bb_middle, bb_lower = calculate_bollinger_bands(close_prices, 20, 2.0)
    indicators['bb_upper'] = bb_upper
    indicators['bb_middle'] = bb_middle
    indicators['bb_lower'] = bb_lower
    
    # Additional indicators if high/low prices are available
    if high_prices is not None and low_prices is not None:
        indicators['stoch_k'], indicators['stoch_d'] = calculate_stochastic(
            high_prices, low_prices, close_prices, 14, 3
        )
        indicators['atr'] = calculate_atr(high_prices, low_prices, close_prices, 14)
    
    return indicators 