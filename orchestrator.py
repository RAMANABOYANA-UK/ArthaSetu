"""
Main CrewAI orchestrator for coordinating multi-agent analysis
"""
from crewai import Crew, Task
from agents.financial_agents import (
    create_market_researcher_agent,
    create_technical_analyst_agent,
    create_sentiment_analyst_agent,
    create_portfolio_strategist_agent
)
from tools.portfolio_analysis import StockRecommendationEngine
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)

class MarketIntelligenceOrchestrator:
    """Orchestrates multi-agent workflow for financial intelligence"""
    
    def __init__(self):
        # Initialize agents
        self.market_researcher = create_market_researcher_agent()
        self.technical_analyst = create_technical_analyst_agent()
        self.sentiment_analyst = create_sentiment_analyst_agent()
        self.portfolio_strategist = create_portfolio_strategist_agent()
    
    def analyze_stock_for_buy(self, symbol: str, portfolio_context: Optional[Dict] = None) -> Dict:
        """
        Comprehensive stock analysis: "Should I buy this stock?"
        Uses all agents to provide multi-factor recommendation
        
        Args:
            symbol: Stock ticker/name (e.g., "TCS", "Infosys")
            portfolio_context: Optional dict with user holdings info
            
        Returns:
            Dict with recommendation, confidence, and detailed reasoning
        """
        try:
            logger.info(f"Starting comprehensive analysis for {symbol}")
            
            # Task 1: Market researcher gathers data
            research_task = Task(
                description=f"""Fetch current market data and fundamentals for {symbol}.
                Provide: current price, daily change, P/E ratio, market cap, and key metrics.""",
                agent=self.market_researcher,
                expected_output="Comprehensive market data for the stock"
            )
            
            # Task 2: Technical analyst does technical analysis
            technical_task = Task(
                description=f"""Perform technical analysis on {symbol} charts (daily and weekly).
                Check for: RSI levels, MACD signals, support/resistance, divergences, and breakouts.
                Provide: signal (BUY/SELL/HOLD) with confidence and reasoning.""",
                agent=self.technical_analyst,
                expected_output="Technical analysis with specific signals and confidence levels"
            )
            
            # Task 3: Sentiment analyst analyzes news
            sentiment_task = Task(
                description=f"""Analyze recent news and sentiment for {symbol}.
                Check for: earnings announcements, analyst upgrades/downgrades, sector trends.
                Provide: overall sentiment (BULLISH/BEARISH/NEUTRAL) with key drivers.""",
                agent=self.sentiment_analyst,
                expected_output="Sentiment analysis with key news drivers"
            )
            
            # Task 4: Portfolio strategist synthesizes
            portfolio_task = Task(
                description=f"""Synthesize the analysis into investment recommendation for {symbol}.
                Consider: technical signals, sentiment, fundamentals, and portfolio context.
                Provide: final BUY/SELL/HOLD with confidence %, key factors, and risk assessment.""",
                agent=self.portfolio_strategist,
                expected_output="Final investment recommendation with confidence and reasoning"
            )
            
            # Create crew
            crew = Crew(
                agents=[self.market_researcher, self.technical_analyst, self.sentiment_analyst, self.portfolio_strategist],
                tasks=[research_task, technical_task, sentiment_task, portfolio_task],
                verbose=True,
                max_iterations=5
            )
            
            # Execute crew workflow
            result = crew.kickoff()
            
            return {
                'status': 'success',
                'symbol': symbol,
                'analysis': str(result),
                'timestamp': pd.Timestamp.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in stock analysis: {str(e)}")
            return {
                'status': 'error',
                'symbol': symbol,
                'error': str(e),
                'timestamp': pd.Timestamp.now().isoformat()
            }
    
    def analyze_portfolio_risk(self, holdings: List[Dict]) -> Dict:
        """
        Analyze portfolio concentration and provide rebalancing suggestions
        
        Args:
            holdings: List of dicts with portfolio positions
            
        Returns:
            Dict with risk assessment and recommendations
        """
        try:
            logger.info(f"Analyzing portfolio with {len(holdings)} holdings")
            
            portfolio_task = Task(
                description=f"""Analyze this portfolio for concentration risk: {holdings}
                Provide: sector breakdown, concentration metrics, risk assessment, and rebalancing suggestions.
                Identify which positions are too large and which sectors are underrepresented.""",
                agent=self.portfolio_strategist,
                expected_output="Portfolio risk analysis with specific rebalancing suggestions"
            )
            
            crew = Crew(
                agents=[self.portfolio_strategist],
                tasks=[portfolio_task],
                verbose=True,
                max_iterations=3
            )
            
            result = crew.kickoff()
            
            return {
                'status': 'success',
                'analysis': str(result),
                'timestamp': pd.Timestamp.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': pd.Timestamp.now().isoformat()
            }
    
    def analyze_sector_rotation(self, sectors: Optional[List[str]] = None) -> Dict:
        """
        Analyze sector momentum and rotation opportunities
        
        Args:
            sectors: Optional list of sectors to analyze (default: major Indian sectors)
            
        Returns:
            Dict with sector momentum analysis and recommendations
        """
        if not sectors:
            sectors = ["IT", "Banking", "Pharma", "Auto", "FMCG", "Utilities"]
        
        try:
            logger.info(f"Analyzing sector rotation across: {sectors}")
            
            rotation_task = Task(
                description=f"""Analyze sector rotation opportunities across: {', '.join(sectors)}.
                Check: sector momentum, PE ratios, earnings growth, FII flows, and relative strength.
                Provide: ranking of attractive sectors and recommend rotation moves.""",
                agent=self.sentiment_analyst,
                expected_output="Sector rotation analysis with specific recommendations"
            )
            
            crew = Crew(
                agents=[self.sentiment_analyst, self.technical_analyst],
                tasks=[rotation_task],
                verbose=True,
                max_iterations=3
            )
            
            result = crew.kickoff()
            
            return {
                'status': 'success',
                'analysis': str(result),
                'timestamp': pd.Timestamp.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error in sector analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'timestamp': pd.Timestamp.now().isoformat()
            }

import pandas as pd
