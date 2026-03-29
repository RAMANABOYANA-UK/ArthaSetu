"""
Configuration management for Market Intelligence Agent
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY", "")

# Model Configuration
LLM_MODEL = "gpt-3.5-turbo"
LLM_TEMPERATURE = 0.3  # Lower temperature for consistent financial analysis

# Agent Configuration
MAX_ITERATIONS = 5
ITERATION_TIMEOUT = 30  # seconds

# Data Configuration
CACHE_DURATION = 300  # 5 minutes
TECHNICAL_INDICATORS = {
    "RSI_PERIOD": 14,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "SMA_FAST": 20,
    "SMA_SLOW": 50,
}

# NSE Stock symbols (sample mapping)
NSE_SYMBOLS_MAPPING = {
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "Reliance": "RELIANCE.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ITC": "ITC.NS",
    "Bajaj Finance": "BAJAJFINSV.NS",
    "Hindustan Unilever": "HINDUNILVR.NS",
    "SBI": "SBIN.NS",
    "Wipro": "WIPRO.NS",
    "Maruti": "MARUTI.NS",
}

# India-specific FII/DII data source (mock for MVP)
FII_TREND = {
    "trend": "bullish",
    "net_flow_today": 500,  # crores
    "sector_preference": ["IT", "Pharma", "Auto"],
    "last_updated": "2024-01-15 15:30:00"
}
