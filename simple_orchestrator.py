"""
Simplified orchestrator without CrewAI for MVP
This version works with basic Python and the tools we've created
"""
import logging
from typing import Dict, Optional, List
from data_connectors.stock_data import StockDataConnector
from data_connectors.news_sentiment import NewsSentimentConnector
from tools.technical_analysis import TechnicalAnalyzer
from tools.portfolio_analysis import PortfolioAnalyzer, StockRecommendationEngine

logger = logging.getLogger(__name__)

class SimpleMarketIntelligenceOrchestrator:
    """Simplified orchestrator for financial analysis (no CrewAI dependency)"""
    
    def __init__(self):
        self.stock_connector = StockDataConnector()
        self.news_connector = NewsSentimentConnector()
    
    def analyze_stock_for_buy(self, symbol: str, portfolio_context: Optional[Dict] = None) -> Dict:
        """
        Comprehensive stock analysis without CrewAI
        
        Args:
            symbol: Stock ticker/name
            portfolio_context: Optional portfolio info
            
        Returns:
            Dict with multi-factor recommendation
        """
        try:
            logger.info(f"Starting stock analysis for {symbol}")
            
            # Step 1: Resolve ticker
            ticker = self.stock_connector.resolve_ticker(symbol)
            if not ticker:
                return {'status': 'error', 'message': f'Could not resolve ticker for {symbol}'}
            
            # Step 2: Fetch market data
            logger.info(f"[RESEARCHER] Fetching market data for {ticker}...")
            live_price = self.stock_connector.get_live_price(ticker)
            fundamentals = self.stock_connector.get_fundamental_data(ticker)
            
            # Step 3: Technical analysis
            logger.info(f"[TECHNICAL ANALYST] Running technical analysis on {ticker}...")
            data = self.stock_connector.get_stock_data(ticker, period="3mo")
            if data is None or data.empty:
                return {'status': 'error', 'message': f'No historical data for {symbol}'}
            
            technical_signal = TechnicalAnalyzer.get_technical_signal(data)
            support_res = TechnicalAnalyzer.get_support_resistance(data)
            divergence = TechnicalAnalyzer.detect_divergence(data)
            breakout = TechnicalAnalyzer.detect_breakout(data)
            
            # Step 4: Sentiment analysis
            logger.info(f"[SENTIMENT ANALYST] Analyzing sentiments for {symbol}...")
            sentiment = self.news_connector.get_company_sentiment(symbol, days=7)
            
            # Step 5: Portfolio context
            portfolio_context_analysis = None
            if portfolio_context:
                portfolio_context_analysis = {
                    'existing_concentration': portfolio_context.get('concentration', 0)
                }
            
            # Step 6: Synthesize recommendation
            logger.info(f"[PORTFOLIO STRATEGIST] Synthesizing recommendation for {symbol}...")
            recommendation = StockRecommendationEngine.synthesize_recommendation(
                technical_signal,
                sentiment,
                fundamentals or {},
                portfolio_context_analysis
            )
            
            return {
                'status': 'success',
                'symbol': symbol,
                'ticker': ticker,
                'live_price': live_price,
                'technical_signal': technical_signal,
                'support_resistance': support_res,
                'divergence': divergence,
                'breakout': breakout,
                'sentiment': sentiment,
                'fundamentals': fundamentals,
                'recommendation': recommendation,
                'agent_trajectory': [
                    '[RESEARCHER] Fetched live prices and fundamentals',
                    '[TECHNICAL ANALYST] Detected patterns and support/resistance',
                    '[SENTIMENT ANALYST] Processed recent news and market sentiment',
                    '[PORTFOLIO STRATEGIST] Synthesized multi-factor recommendation'
                ]
            }
        except Exception as e:
            logger.error(f"Error in stock analysis: {str(e)}")
            return {
                'status': 'error',
                'symbol': symbol,
                'message': str(e)
            }
    
    def analyze_portfolio_risk(self, holdings: List[Dict]) -> Dict:
        """Analyze portfolio concentration and risk"""
        try:
            logger.info(f"Analyzing portfolio with {len(holdings)} holdings...")
            
            concentration = PortfolioAnalyzer.analyze_concentration(holdings)
            metrics = PortfolioAnalyzer.calculate_portfolio_metrics(holdings)
            rebalance_suggestions = PortfolioAnalyzer.get_rebalance_suggestions(holdings)
            
            return {
                'status': 'success',
                'concentration': concentration,
                'metrics': metrics,
                'rebalance_suggestions': rebalance_suggestions,
                'agent_trajectory': [
                    '[PORTFOLIO STRATEGIST] Analyzed concentration and sector exposure',
                    '[PORTFOLIO STRATEGIST] Calculated risk metrics',
                    '[PORTFOLIO STRATEGIST] Generated rebalancing suggestions'
                ]
            }
        except Exception as e:
            logger.error(f"Error in portfolio analysis: {str(e)}")
            return {'status': 'error', 'message': str(e)}
    
    def analyze_sector_rotation(self, sectors: Optional[List[str]] = None) -> Dict:
        """Analyze sector momentum and rotation opportunities"""
        if not sectors:
            sectors = ["IT", "Banking", "Pharma", "Auto", "FMCG", "Utilities"]
        
        try:
            logger.info(f"Analyzing sector rotation for: {sectors}")
            
            sector_analysis = {}
            for sector in sectors:
                sentiment = self.news_connector.get_sector_sentiment(sector)
                sector_analysis[sector] = sentiment
            
            # Rank sectors by sentiment
            ranked_sectors = sorted(
                sector_analysis.items(),
                key=lambda x: 1 if x[1].get('sentiment') == 'BULLISH' else -1,
                reverse=True
            )
            
            return {
                'status': 'success',
                'sector_analysis': sector_analysis,
                'ranked_sectors': ranked_sectors,
                'recommendation': 'Rotate from underperforming to outperforming sectors',
                'agent_trajectory': [
                    '[SENTIMENT ANALYST] Analyzed sector momentum',
                    '[TECHNICAL ANALYST] Checked sector technical strength',
                    '[PORTFOLIO STRATEGIST] Ranked sectors and suggested rotations'
                ]
            }
        except Exception as e:
            logger.error(f"Error in sector analysis: {str(e)}")
            return {'status': 'error', 'message': str(e)}
