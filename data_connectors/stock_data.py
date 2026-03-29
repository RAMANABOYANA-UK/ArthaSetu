"""
Stock data connector using yfinance for NSE/BSE stocks and global markets
"""
import yfinance as yf
import pandas as pd
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class StockDataConnector:
    """Fetch and cache stock data from yfinance"""
    
    def __init__(self):
        self.cache = {}
        
    def resolve_ticker(self, symbol: str, market: str = "NSE") -> Optional[str]:
        """
        Resolve company name or NSE symbol to yfinance ticker
        
        Args:
            symbol: Company name or ticker (e.g., "TCS", "Infosys", "INFY")
            market: "NSE", "BSE", or "GLOBAL"
            
        Returns:
            yfinance ticker string or None
        """
        from config import NSE_SYMBOLS_MAPPING
        
        if market == "NSE":
            # Try direct mapping
            if symbol in NSE_SYMBOLS_MAPPING:
                return NSE_SYMBOLS_MAPPING[symbol]
            # Handle uppercase/lowercase variants
            if symbol.upper() in NSE_SYMBOLS_MAPPING:
                return NSE_SYMBOLS_MAPPING[symbol.upper()]
            # If not in mapping, assume it's already a valid NSE ticker format
            if symbol.endswith(".NS"):
                return symbol
            return f"{symbol}.NS"
        elif market == "GLOBAL":
            return symbol  # Assume valid ticker for global markets
        return None

    def get_stock_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data
        
        Args:
            symbol: yfinance ticker (e.g., "TCS.NS")
            period: "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"
            interval: "1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo"
            
        Returns:
            DataFrame with OHLCV data or None if error
        """
        try:
            cache_key = f"{symbol}_{period}_{interval}"
            if cache_key in self.cache:
                return self.cache[cache_key]
                
            data = yf.download(symbol, period=period, interval=interval, progress=False)
            if data is not None and not data.empty:
                self.cache[cache_key] = data
                return data
            return None
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def get_live_price(self, symbol: str) -> Optional[Dict]:
        """
        Get live/latest stock price and basic info
        
        Args:
            symbol: yfinance ticker
            
        Returns:
            Dict with current price, change, volume, market cap or None
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            
            if data.empty:
                return None
                
            latest = data.iloc[-1]
            info = ticker.info
            
            return {
                "symbol": symbol,
                "current_price": float(latest['Close']) if 'Close' in latest else None,
                "previous_close": float(latest['Open']) if 'Open' in latest else None,
                "volume": int(latest['Volume']) if 'Volume' in latest else 0,
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "dividend_yield": info.get('dividendYield', 'N/A'),
                "fifty_two_week_high": info.get('fiftyTwoWeekHigh', 'N/A'),
                "fifty_two_week_low": info.get('fiftyTwoWeekLow', 'N/A'),
            }
        except Exception as e:
            logger.error(f"Error fetching live price for {symbol}: {str(e)}")
            return None

    def get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Get fundamental company data
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                "company_name": info.get('longName', 'N/A'),
                "sector": info.get('sector', 'N/A'),
                "industry": info.get('industry', 'N/A'),
                "market_cap": info.get('marketCap', 'N/A'),
                "pe_ratio": info.get('trailingPE', 'N/A'),
                "eps": info.get('trailingEps', 'N/A'),
                "revenue": info.get('totalRevenue', 'N/A'),
                "profit_margin": info.get('profitMargins', 'N/A'),
                "roe": info.get('returnOnEquity', 'N/A'),
                "debt_to_equity": info.get('debtToEquity', 'N/A'),
            }
        except Exception as e:
            logger.error(f"Error fetching fundamentals for {symbol}: {str(e)}")
            return None

    def get_price_change(self, symbol: str, period: str = "1d") -> Optional[Tuple[float, float]]:
        """
        Get price change percentage for a period
        
        Returns:
            Tuple of (change_amount, change_percentage) or None
        """
        try:
            data = self.get_stock_data(symbol, period=period)
            if data is None or len(data) < 2:
                return None
                
            first_close = float(data.iloc[0]['Close'])
            last_close = float(data.iloc[-1]['Close'])
            change = last_close - first_close
            change_pct = (change / first_close) * 100
            return (change, change_pct)
        except Exception as e:
            logger.error(f"Error calculating price change: {str(e)}")
            return None
