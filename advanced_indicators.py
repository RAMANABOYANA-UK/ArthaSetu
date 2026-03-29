"""
Advanced Technical Indicators Module
RSI, MACD, Bollinger Bands, Volume Analysis, Support/Resistance
"""

import yfinance as yf
import random

def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    RSI > 70 = Overbought (potential sell)
    RSI < 30 = Oversold (potential buy)
    """
    if len(prices) < period:
        return 50
    
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    gains = [d if d > 0 else 0 for d in deltas]
    losses = [-d if d < 0 else 0 for d in deltas]
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    MACD > Signal = Bullish
    MACD < Signal = Bearish
    """
    if len(prices) < slow:
        return {'macd': 0, 'signal': 0, 'histogram': 0}
    
    # Calculate exponential moving averages
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    
    macd = ema_fast - ema_slow
    
    # Signal line is EMA of MACD
    macd_values = []
    for i in range(len(prices) - slow):
        ema_f = calculate_ema(prices[i:i+fast+1], fast)
        ema_s = calculate_ema(prices[i:i+slow+1], slow)
        macd_values.append(ema_f - ema_s)
    
    signal_line = calculate_ema(macd_values[-signal:], signal) if len(macd_values) >= signal else macd
    histogram = macd - signal_line
    
    return {
        'macd': round(macd, 4),
        'signal': round(signal_line, 4),
        'histogram': round(histogram, 4),
        'signal': 'BULLISH' if macd > signal_line else 'BEARISH'
    }

def calculate_ema(prices, period):
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return sum(prices) / len(prices)
    
    multiplier = 2 / (period + 1)
    sma = sum(prices[-period:]) / period
    ema = sma
    
    for price in prices[-period+1:]:
        ema = (price * multiplier) + (ema * (1 - multiplier))
    
    return ema

def calculate_bollinger_bands(prices, period=20, std_dev=2):
    """
    Calculate Bollinger Bands
    Upper Band = SMA + (StdDev * 2)
    Lower Band = SMA - (StdDev * 2)
    """
    if len(prices) < period:
        return {'upper': 0, 'middle': 0, 'lower': 0, 'position': 'MIDDLE'}
    
    sma = sum(prices[-period:]) / period
    
    # Calculate standard deviation
    variance = sum((p - sma) ** 2 for p in prices[-period:]) / period
    std = variance ** 0.5
    
    upper_band = sma + (std_dev * std)
    lower_band = sma - (std_dev * std)
    
    current_price = prices[-1]
    
    # Determine position within bands
    if current_price > upper_band:
        position = 'OVERBOUGHT'
    elif current_price < lower_band:
        position = 'OVERSOLD'
    else:
        position = 'NORMAL'
    
    return {
        'upper_band': round(upper_band, 2),
        'middle_band': round(sma, 2),
        'lower_band': round(lower_band, 2),
        'current_price': round(current_price, 2),
        'position': position,
        'band_width': round(((upper_band - lower_band) / sma) * 100, 2)
    }

def calculate_support_resistance(prices, period=20):
    """
    Identify key support and resistance levels
    Support = Local low points
    Resistance = Local high points
    """
    if len(prices) < period:
        return {}
    
    recent_prices = prices[-period:]
    min_price = min(recent_prices)
    max_price = max(recent_prices)
    
    current = recent_prices[-1]
    
    # Calculate levels
    pivot = (max_price + min_price + current) / 3
    resistance1 = (2 * pivot) - min_price
    support1 = (2 * pivot) - max_price
    resistance2 = pivot + (max_price - min_price)
    support2 = pivot - (max_price - min_price)
    
    return {
        'support_2': round(support2, 2),
        'support_1': round(support1, 2),
        'pivot': round(pivot, 2),
        'resistance_1': round(resistance1, 2),
        'resistance_2': round(resistance2, 2),
        'current_price': round(current, 2),
        'nearest_resistance': round(resistance1, 2),
        'nearest_support': round(support1, 2)
    }

def calculate_volume_analysis(volumes, period=20):
    """
    Analyze trading volume trends
    High volume breakout = Strong move
    Low volume pullback = Weak move
    """
    if len(volumes) < period:
        return {}
    
    avg_volume = sum(volumes[-period:]) / period
    current_volume = volumes[-1]
    
    volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
    
    if volume_ratio > 1.5:
        volume_signal = 'HIGH'
        interpretation = 'Strong move expected'
    elif volume_ratio > 1.0:
        volume_signal = 'ABOVE_AVERAGE'
        interpretation = 'Moderate strength'
    elif volume_ratio > 0.5:
        volume_signal = 'BELOW_AVERAGE'
        interpretation = 'Weak move, lack of conviction'
    else:
        volume_signal = 'LOW'
        interpretation = 'Very weak volume'
    
    return {
        'current_volume': int(current_volume),
        'avg_volume': int(avg_volume),
        'volume_ratio': round(volume_ratio, 2),
        'signal': volume_signal,
        'interpretation': interpretation
    }

def get_advanced_indicators(symbol, current_price=None):
    """
    Comprehensive advanced technical analysis for a stock
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='90d')
        
        if hist.empty or len(hist) < 20:
            return generate_mock_indicators()
        
        prices = hist['Close'].tolist()
        volumes = hist['Volume'].tolist()
        
        # Calculate all indicators
        indicators = {
            'rsi': calculate_rsi(prices),
            'rsi_signal': 'OVERBOUGHT' if calculate_rsi(prices) > 70 else ('OVERSOLD' if calculate_rsi(prices) < 30 else 'NEUTRAL'),
            'macd': calculate_macd(prices),
            'bollinger_bands': calculate_bollinger_bands(prices),
            'support_resistance': calculate_support_resistance(prices),
            'volume_analysis': calculate_volume_analysis(volumes),
            'current_price': round(prices[-1], 2),
            'price_trend': determine_trend(prices, 20)
        }
        
        return indicators
    except:
        return generate_mock_indicators()

def generate_mock_indicators():
    """Generate mock indicators when API fails"""
    return {
        'rsi': random.uniform(30, 70),
        'rsi_signal': 'NEUTRAL',
        'macd': {
            'macd': round(random.uniform(-5, 5), 4),
            'signal': round(random.uniform(-5, 5), 4),
            'histogram': round(random.uniform(-2, 2), 4),
            'signal': 'BULLISH' if random.random() > 0.5 else 'BEARISH'
        },
        'bollinger_bands': {
            'upper_band': 2500,
            'middle_band': 2400,
            'lower_band': 2300,
            'current_price': 2390,
            'position': 'NORMAL',
            'band_width': 4.17
        },
        'support_resistance': {
            'support_2': 2250,
            'support_1': 2325,
            'pivot': 2400,
            'resistance_1': 2475,
            'resistance_2': 2550,
            'current_price': 2390
        },
        'volume_analysis': {
            'signal': 'ABOVE_AVERAGE',
            'volume_ratio': 1.2
        },
        'price_trend': 'UPTREND'
    }

def determine_trend(prices, period=20):
    """Determine if stock is in uptrend, downtrend, or sideways"""
    if len(prices) < period:
        return 'NEUTRAL'
    
    recent = prices[-period:]
    old_avg = sum(recent[:period//2]) / (period//2)
    new_avg = sum(recent[period//2:]) / (period//2)
    
    if new_avg > old_avg * 1.02:
        return 'UPTREND'
    elif new_avg < old_avg * 0.98:
        return 'DOWNTREND'
    else:
        return 'SIDEWAYS'

def get_trading_signals(symbol):
    """Generate trading signals based on all technical indicators"""
    indicators = get_advanced_indicators(symbol)
    
    signals = {
        'rsi_signal': 'BUY' if indicators.get('rsi', 50) < 30 else ('SELL' if indicators.get('rsi', 50) > 70 else 'NEUTRAL'),
        'macd_signal': indicators.get('macd', {}).get('signal', 'NEUTRAL'),
        'bb_signal': 'BUY' if indicators.get('bollinger_bands', {}).get('position') == 'OVERSOLD' else ('SELL' if indicators.get('bollinger_bands', {}).get('position') == 'OVERBOUGHT' else 'NEUTRAL'),
        'trend_signal': 'BUY' if indicators.get('price_trend') == 'UPTREND' else ('SELL' if indicators.get('price_trend') == 'DOWNTREND' else 'NEUTRAL'),
        'volume_signal': 'STRONG' if indicators.get('volume_analysis', {}).get('signal') == 'HIGH' else 'WEAK'
    }
    
    # Generate consensus signal
    buy_signals = sum(1 for s in signals.values() if s == 'BUY')
    sell_signals = sum(1 for s in signals.values() if s == 'SELL')
    
    if buy_signals > sell_signals:
        consensus = 'BUY'
    elif sell_signals > buy_signals:
        consensus = 'SELL'
    else:
        consensus = 'HOLD'
    
    return {
        'individual_signals': signals,
        'consensus_signal': consensus,
        'signal_strength': max(buy_signals, sell_signals),
        'all_indicators': indicators
    }
