"""
CrewAI agent definitions for financial analysis
"""
from crewai import Agent
from crewai_tools import tool
from data_connectors.stock_data import StockDataConnector
from data_connectors.news_sentiment import NewsSentimentConnector
from tools.technical_analysis import TechnicalAnalyzer
from tools.portfolio_analysis import PortfolioAnalyzer, StockRecommendationEngine
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Initialize data connectors
stock_connector = StockDataConnector()
news_connector = NewsSentimentConnector()

# ==================== Agent Tools ====================

@tool("See current stock price and daily data")
def fetch_stock_price(symbol: str) -> str:
    """Fetch current stock price and daily data for a given symbol"""
    try:
        ticker = stock_connector.resolve_ticker(symbol)
        if not ticker:
            return f"Could not resolve ticker for {symbol}"
        
        data = stock_connector.get_stock_data(ticker, period="1d")
        if data is None:
            return f"No data available for {symbol}"
        
        live_data = stock_connector.get_live_price(ticker)
        if not live_data:
            return f"Could not fetch live price for {symbol}"
        
        return f"""
        Stock: {symbol} ({ticker})
        Current Price: ₹{live_data['current_price']:.2f}
        Day Change: {((live_data['current_price'] - live_data['previous_close']) / live_data['previous_close'] * 100):.2f}%
        Volume: {live_data['volume']:,.0f}
        Market Cap: {live_data['market_cap']}
        P/E Ratio: {live_data['pe_ratio']}
        52-Week High: {live_data['fifty_two_week_high']}
        52-Week Low: {live_data['fifty_two_week_low']}
        """
    except Exception as e:
        return f"Error fetching price for {symbol}: {str(e)}"

@tool("Get multi-timeframe technical analysis")
def analyze_technical_patterns(symbol: str, timeframes: Optional[List[str]] = None) -> str:
    """Analyze technical patterns for a stock across multiple timeframes"""
    try:
        ticker = stock_connector.resolve_ticker(symbol)
        if not ticker:
            return f"Invalid ticker: {symbol}"
        
        if not timeframes:
            timeframes = ["1d", "1wk"]  # Default: daily and weekly
        
        analysis_results = []
        for timeframe in timeframes:
            data = stock_connector.get_stock_data(ticker, period="3mo", interval=timeframe)
            if data is None or data.empty:
                continue
            
            signal = TechnicalAnalyzer.get_technical_signal(data)
            support_res = TechnicalAnalyzer.get_support_resistance(data)
            
            analysis_results.append(f"""
            === {timeframe.upper()} Chart ===
            Signal: {signal['signal']} (Confidence: {signal['confidence']:.0%})
            RSI: {signal['rsi']:.0f}
            Reasoning: {signal.get('reasoning', 'Mixed signals')}
            
            Support: {support_res['support']:.2f}
            Resistance: {support_res['resistance']:.2f}
            Pivot: {support_res['pivot']:.2f}
            """)
        
        return "\n".join(analysis_results)
    except Exception as e:
        return f"Error in technical analysis for {symbol}: {str(e)}"

@tool("Get recent news and sentiment")
def get_sentiment_analysis(symbol: str) -> str:
    """Get recent news and sentiment analysis for a stock"""
    try:
        company_name = symbol.replace(".NS", "").upper()
        sentiment = news_connector.get_company_sentiment(company_name, days=7)
        
        return f"""
        Sentiment: {sentiment['sentiment']} (Score: {sentiment['score']:.2f})
        Articles Analyzed: {sentiment['articles_analyzed']}
        
        Analysis: {sentiment['reasoning']}
        
        Top Articles:
        {chr(10).join([f"- {article['title'][:60]}... ({article['source']})" for article in sentiment.get('top_articles', [])])}
        """
    except Exception as e:
        return f"Error getting sentiment for {symbol}: {str(e)}"

@tool("Get fundamental company data")
def get_fundamentals(symbol: str) -> str:
    """Get fundamental company data like P/E, market cap, ROE, etc."""
    try:
        ticker = stock_connector.resolve_ticker(symbol)
        if not ticker:
            return f"Invalid ticker: {symbol}"
        
        fundamentals = stock_connector.get_fundamental_data(ticker)
        if not fundamentals:
            return f"No fundamental data available for {symbol}"
        
        return f"""
        Company: {fundamentals.get('company_name', 'N/A')}
        Sector: {fundamentals.get('sector', 'N/A')}
        Industry: {fundamentals.get('industry', 'N/A')}
        
        Market Cap: {fundamentals.get('market_cap', 'N/A')}
        P/E Ratio: {fundamentals.get('pe_ratio', 'N/A')}
        EPS: {fundamentals.get('eps', 'N/A')}
        
        Profitability:
        - Profit Margin: {fundamentals.get('profit_margin', 'N/A')}
        - ROE: {fundamentals.get('roe', 'N/A')}
        
        Debt Metrics:
        - Debt to Equity: {fundamentals.get('debt_to_equity', 'N/A')}
        """
    except Exception as e:
        return f"Error getting fundamentals for {symbol}: {str(e)}"

@tool("Analyze portfolio risk")
def analyze_portfolio_risk(holdings: List[Dict]) -> str:
    """Analyze portfolio concentration and risk"""
    try:
        concentration = PortfolioAnalyzer.analyze_concentration(holdings)
        
        return f"""
        === Portfolio Risk Analysis ===
        Total Value: ₹{concentration.get('total_portfolio_value', 0):,.0f}
        Concentration Risk: {concentration.get('concentration_risk', 'UNKNOWN')}
        Max Sector Weight: {concentration.get('max_sector_weight', 0):.1f}%
        
        Sector Breakdown:
        {chr(10).join([f"- {sector}: {weight:.1f}%" for sector, weight in concentration.get('sector_breakdown', {}).items()])}
        
        Recommendation: {concentration.get('recommendation', 'N/A')}
        
        Top 3 Positions:
        {chr(10).join([f"- {pos['symbol']}: {pos['weight']:.1f}% (₹{pos['value']:,.0f})" for pos in concentration.get('top_positions', [])])}
        """
    except Exception as e:
        return f"Error analyzing portfolio: {str(e)}"

# ==================== Agent Definitions ====================

def create_market_researcher_agent() -> Agent:
    """Agent responsible for fetching market data and company fundamentals"""
    return Agent(
        role="Market Data Researcher",
        goal="Gather real-time market data, stock prices, fundamentals, and key metrics for analysis",
        backstory="""You are an expert market researcher specializing in Indian stock markets. 
        You have deep knowledge of NSE/BSE stocks, company fundamentals, and market data interpretation.
        Your role is to fetch accurate, current data and present it in a clear, organized manner.""",
        tools=[fetch_stock_price, get_fundamentals],
        verbose=True,
        allow_delegation=False
    )

def create_technical_analyst_agent() -> Agent:
    """Agent responsible for technical analysis and pattern detection"""
    return Agent(
        role="Technical Analyst",
        goal="Analyze charts, detect technical patterns, and identify entry/exit signals",
        backstory="""You are an experienced technical analyst with expertise in identifying chart patterns,
        support/resistance levels, RSI divergences, MACD crossovers, and breakouts.
        You specialize in multi-timeframe analysis and have helped thousands of retail investors
        time their market entries and exits correctly.""",
        tools=[analyze_technical_patterns],
        verbose=True,
        allow_delegation=False
    )

def create_sentiment_analyst_agent() -> Agent:
    """Agent responsible for news and sentiment analysis"""
    return Agent(
        role="Sentiment Analyst",
        goal="Analyze market sentiment, news, earnings, and institutional flows",
        backstory="""You are a sentiment analysis expert who follows financial markets closely.
        You understand how news impacts stock prices and can identify market sentiment shifts.
        You track earnings announcements, FII flows, sector rotations, and policy changes.""",
        tools=[get_sentiment_analysis],
        verbose=True,
        allow_delegation=False
    )

def create_portfolio_strategist_agent() -> Agent:
    """Agent responsible for portfolio analysis and recommendations"""
    return Agent(
        role="Portfolio Risk Strategist",
        goal="Assess portfolio risk, identify concentration issues, and provide actionable recommendations",
        backstory="""You are a senior portfolio manager with 15+ years of experience.
        You specialize in risk management, portfolio optimization, and return maximization.
        You understand sector correlations, currency exposure, and institutional positioning.""",
        tools=[analyze_portfolio_risk],
        verbose=True,
        allow_delegation=False
    )
