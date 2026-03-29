"""
Technical analysis tools for chart pattern detection and indicator calculation
"""
import pandas as pd
import numpy as np
import ta  # Technical Analysis library
from typing import Dict, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Detect technical patterns and calculate indicators"""
    
    @staticmethod
    def calculate_rsi(data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            close = data['Close'].squeeze() if isinstance(data['Close'], pd.DataFrame) else data['Close']
            return ta.momentum.rsi(close, window=period)
        except Exception as e:
            logger.error(f"RSI calculation error: {str(e)}")
            return pd.Series(dtype=float)
    
    @staticmethod
    def calculate_macd(data: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> Dict:
        """Calculate MACD and signal line"""
        try:
            close = data['Close'].squeeze() if isinstance(data['Close'], pd.DataFrame) else data['Close']
            macd = ta.trend.macd(close, window_fast=fast, window_slow=slow)
            return {
                'macd': macd.iloc[:, 0] if isinstance(macd, pd.DataFrame) else macd,
                'signal': macd.iloc[:, 1] if isinstance(macd, pd.DataFrame) and len(macd.columns) > 1 else pd.Series(),
                'histogram': macd.iloc[:, 2] if isinstance(macd, pd.DataFrame) and len(macd.columns) > 2 else pd.Series()
            }
        except Exception as e:
            logger.error(f"MACD calculation error: {str(e)}")
            return {'macd': pd.Series(), 'signal': pd.Series(), 'histogram': pd.Series()}
    
    @staticmethod
    def calculate_moving_averages(data: pd.DataFrame, fast: int = 20, slow: int = 50) -> Dict:
        """Calculate SMA (Simple Moving Averages)"""
        try:
            close = data['Close'].squeeze() if isinstance(data['Close'], pd.DataFrame) else data['Close']
            return {
                'sma_fast': ta.trend.sma_indicator(close, window=fast),
                'sma_slow': ta.trend.sma_indicator(close, window=slow)
            }
        except Exception as e:
            logger.error(f"SMA calculation error: {str(e)}")
            return {'sma_fast': pd.Series(), 'sma_slow': pd.Series()}
    
    @staticmethod
    def calculate_bollinger_bands(data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        """Calculate Bollinger Bands"""
        try:
            bb = ta.volatility.BollingerBands(data['Close'], window=period, window_dev=std_dev)
            return {
                'upper_band': bb.bollinger_hband(),
                'middle_band': bb.bollinger_mavg(),
                'lower_band': bb.bollinger_lband()
            }
        except Exception as e:
            logger.error(f"Bollinger Bands error: {str(e)}")
            return {'upper_band': pd.Series(), 'middle_band': pd.Series(), 'lower_band': pd.Series()}
    
    @staticmethod
    def get_support_resistance(data: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Calculate support and resistance levels
        """
        try:
            highs = data['High'].tail(lookback)
            lows = data['Low'].tail(lookback)
            closes = data['Close'].tail(lookback)
            
            resistance = highs.max()
            support = lows.min()
            pivot = (highs.max() + lows.min() + closes.iloc[-1]) / 3
            
            return {
                'resistance': float(resistance),
                'support': float(support),
                'pivot': float(pivot),
                'range': float(resistance - support)
            }
        except Exception as e:
            logger.error(f"Support/Resistance error: {str(e)}")
            return {'resistance': 0, 'support': 0, 'pivot': 0, 'range': 0}
    
    @staticmethod
    def detect_divergence(data: pd.DataFrame, period: int = 14) -> Dict:
        """
        Detect RSI divergences (bullish/bearish)
        """
        try:
            rsi = TechnicalAnalyzer.calculate_rsi(data, period)
            closes = data['Close']
            
            if len(rsi) < 2 or len(closes) < 2:
                return {'divergence_type': 'NONE', 'strength': 0}
            
            # Check recent highs/lows
            recent_price_high = closes.iloc[-5:].max()
            recent_price_low = closes.iloc[-5:].min()
            recent_rsi_high = rsi.iloc[-5:].max()
            recent_rsi_low = rsi.iloc[-5:].min()
            
            # Bullish divergence: price makes lower low but RSI makes higher low
            if closes.iloc[-1] < recent_price_low and rsi.iloc[-1] > recent_rsi_low:
                return {
                    'divergence_type': 'BULLISH',
                    'strength': 0.7,
                    'description': 'Price made lower low but RSI holding higher - potential reversal'
                }
            
            # Bearish divergence: price makes higher high but RSI makes lower high
            if closes.iloc[-1] > recent_price_high and rsi.iloc[-1] < recent_rsi_high:
                return {
                    'divergence_type': 'BEARISH',
                    'strength': 0.7,
                    'description': 'Price made higher high but RSI weaker - potential reversal'
                }
            
            return {'divergence_type': 'NONE', 'strength': 0, 'description': 'No significant divergence'}
        except Exception as e:
            logger.error(f"Divergence detection error: {str(e)}")
            return {'divergence_type': 'NONE', 'strength': 0}
    
    @staticmethod
    def detect_breakout(data: pd.DataFrame, lookback: int = 20, sensitivity: float = 0.02) -> Dict:
        """
        Detect bullish/bearish breakouts
        """
        try:
            support_res = TechnicalAnalyzer.get_support_resistance(data, lookback)
            current_price = float(data['Close'].iloc[-1])
            
            resistance = support_res['resistance']
            support = support_res['support']
            
            # Bullish breakout: price breaks above resistance
            if current_price > resistance * (1 + sensitivity):
                return {
                    'pattern': 'BULLISH_BREAKOUT',
                    'confidence': 0.75,
                    'description': f'Price breaking above resistance at {resistance:.2f}',
                    'target': resistance * 1.05
                }
            
            # Bearish breakout: price breaks below support
            if current_price < support * (1 - sensitivity):
                return {
                    'pattern': 'BEARISH_BREAKOUT',
                    'confidence': 0.75,
                    'description': f'Price breaking below support at {support:.2f}',
                    'target': support * 0.95
                }
            
            return {'pattern': 'NO_BREAKOUT', 'confidence': 0}
        except Exception as e:
            logger.error(f"Breakout detection error: {str(e)}")
            return {'pattern': 'NO_BREAKOUT', 'confidence': 0}
    
    @staticmethod
    def get_technical_signal(data: pd.DataFrame) -> Dict:
        """
        Generate overall technical signal combining multiple indicators
        
        Returns:
            Dict with signal (BUY/SELL/HOLD), confidence, and reasoning
        """
        try:
            rsi = TechnicalAnalyzer.calculate_rsi(data)
            macd = TechnicalAnalyzer.calculate_macd(data)
            moving_avgs = TechnicalAnalyzer.calculate_moving_averages(data)
            divergence = TechnicalAnalyzer.detect_divergence(data)
            breakout = TechnicalAnalyzer.detect_breakout(data)
            
            signals = []
            weights = []
            
            # RSI signal
            if not rsi.empty:
                current_rsi = rsi.iloc[-1]
                if current_rsi < 30:
                    signals.append(1)  # Oversold = BUY
                    weights.append(0.3)
                elif current_rsi > 70:
                    signals.append(-1)  # Overbought = SELL
                    weights.append(0.3)
                else:
                    signals.append(0)  # Neutral
                    weights.append(0.2)
            
            # MACD signal
            if not macd['macd'].empty and not macd['signal'].empty:
                macd_hist = macd['histogram'].iloc[-1]
                if macd_hist > 0:
                    signals.append(1)  # MACD bullish
                    weights.append(0.25)
                else:
                    signals.append(-1)  # MACD bearish
                    weights.append(0.25)
            
            # Moving average signal
            if not moving_avgs['sma_fast'].empty:
                current_price = data['Close'].iloc[-1]
                sma_fast = moving_avgs['sma_fast'].iloc[-1]
                sma_slow = moving_avgs['sma_slow'].iloc[-1]
                
                if current_price > sma_fast > sma_slow:
                    signals.append(1)  # Bullish alignment
                    weights.append(0.25)
                elif current_price < sma_fast < sma_slow:
                    signals.append(-1)  # Bearish alignment
                    weights.append(0.25)
                else:
                    signals.append(0)  # Mixed signals
                    weights.append(0.2)
            
            # Calculate weighted signal
            if signals and weights:
                weighted_signal = sum(s * w for s, w in zip(signals, weights)) / sum(weights)
            else:
                weighted_signal = 0
            
            # Classify signal
            if weighted_signal > 0.3:
                signal = "BUY"
                confidence = min(0.9, 0.5 + weighted_signal)
            elif weighted_signal < -0.3:
                signal = "SELL"
                confidence = min(0.9, 0.5 - weighted_signal)
            else:
                signal = "HOLD"
                confidence = 0.5 + abs(weighted_signal)
            
            # Build reasoning
            reasoning = []
            if not rsi.empty and rsi.iloc[-1] < 30:
                reasoning.append(f"RSI ({rsi.iloc[-1]:.1f}) suggests oversold conditions")
            if not rsi.empty and rsi.iloc[-1] > 70:
                reasoning.append(f"RSI ({rsi.iloc[-1]:.1f}) suggests overbought conditions")
            
            if divergence['divergence_type'] != 'NONE':
                reasoning.append(f"{divergence['divergence_type']} divergence detected")
            
            if breakout['pattern'] != 'NO_BREAKOUT':
                reasoning.append(f"{breakout['pattern'].replace('_', ' ')} detected")
            
            return {
                'signal': signal,
                'confidence': confidence,
                'reasoning': "; ".join(reasoning) if reasoning else "Mixed technical signals",
                'rsi': float(rsi.iloc[-1]) if not rsi.empty else 50,
                'divergence': divergence,
                'breakout': breakout
            }
        except Exception as e:
            logger.error(f"Technical signal error: {str(e)}")
            return {
                'signal': 'HOLD',
                'confidence': 0.5,
                'reasoning': 'Unable to calculate technical signals',
                'rsi': 50
            }
