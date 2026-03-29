"""
Portfolio analysis tools for risk assessment and recommendation
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class PortfolioAnalyzer:
    """Analyze portfolio risk and provide recommendations"""
    
    @staticmethod
    def analyze_concentration(holdings: List[Dict]) -> Dict:
        """
        Analyze sector and stock concentration in portfolio
        
        Args:
            holdings: List of dicts with 'symbol', 'quantity', 'entry_price'
            
        Returns:
            Dict with concentration metrics
        """
        if not holdings:
            return {'total_value': 0, 'concentration_risk': 'LOW'}
        
        try:
            # Calculate portfolio value
            portfolio_data = []
            for holding in holdings:
                portfolio_data.append({
                    'symbol': holding['symbol'],
                    'sector': holding.get('sector', 'Unknown'),
                    'value': holding.get('quantity', 0) * holding.get('current_price', 0)
                })
            
            df = pd.DataFrame(portfolio_data)
            total_value = df['value'].sum()
            
            # Calculate position weights
            df['weight'] = (df['value'] / total_value * 100) if total_value > 0 else 0
            
            # Sector concentration
            sector_weights = df.groupby('sector')['weight'].sum().to_dict()
            max_sector_weight = max(sector_weights.values()) if sector_weights else 0
            
            # Risk assessment
            if max_sector_weight > 40:
                concentration_risk = "HIGH"
                recommendation = f"High sector concentration: {max_sector_weight:.1f}% in largest sector. Consider diversifying."
            elif max_sector_weight > 30:
                concentration_risk = "MEDIUM"
                recommendation = f"Moderate sector concentration: {max_sector_weight:.1f}%. May want to rebalance."
            else:
                concentration_risk = "LOW"
                recommendation = "Portfolio well-diversified across sectors."
            
            return {
                'total_portfolio_value': total_value,
                'concentration_risk': concentration_risk,
                'max_sector_weight': max_sector_weight,
                'sector_breakdown': sector_weights,
                'top_positions': df.nlargest(3, 'weight')[['symbol', 'weight', 'value']].to_dict('records'),
                'recommendation': recommendation
            }
        except Exception as e:
            logger.error(f"Concentration analysis error: {str(e)}")
            return {'concentration_risk': 'UNKNOWN'}
    
    @staticmethod
    def calculate_portfolio_metrics(holdings: List[Dict], benchmark_return: float = 0.12) -> Dict:
        """
        Calculate portfolio-level risk metrics
        
        Args:
            holdings: Portfolio holdings
            benchmark_return: Expected annual return (default 12% for Indian market)
            
        Returns:
            Dict with volatility, Sharpe ratio, expected returns
        """
        try:
            if not holdings or len(holdings) < 2:
                return {'volatility': 0, 'sharpe_ratio': 0}
            
            # Simplified volatility calculation
            returns = [h.get('return_pct', 0) for h in holdings]
            returns_array = np.array(returns)
            
            volatility = float(np.std(returns_array))
            expected_return = float(np.mean(returns_array))
            
            # Sharpe ratio (simplified, assuming 0% risk-free rate)
            sharpe_ratio = expected_return / volatility if volatility > 0 else 0
            
            return {
                'portfolio_volatility': volatility,
                'expected_return': expected_return,
                'sharpe_ratio': sharpe_ratio,
                'downside_risk': max(0, -np.percentile(returns_array, 10))
            }
        except Exception as e:
            logger.error(f"Portfolio metrics error: {str(e)}")
            return {'volatility': 0, 'sharpe_ratio': 0}
    
    @staticmethod
    def get_rebalance_suggestions(holdings: List[Dict]) -> Dict:
        """
        Suggest portfolio rebalancing actions
        
        Returns:
            Dict with reduce/add recommendations
        """
        analysis = PortfolioAnalyzer.analyze_concentration(holdings)
        
        suggestions = {
            'reduce': [],
            'add': [],
            'rationale': ''
        }
        
        if analysis.get('concentration_risk') == 'HIGH':
            # Suggest reducing top positions
            top_positions = analysis.get('top_positions', [])
            for pos in top_positions[:2]:
                suggestions['reduce'].append({
                    'symbol': pos['symbol'],
                    'current_weight': pos['weight'],
                    'target_weight': 10,
                    'action': 'Trim to 10% to reduce concentration risk'
                })
            
            suggestions['add'].append({
                'sector': 'Defensive',
                'rationale': 'Add defensive sectors (FMCG, Utility) to reduce volatility'
            })
            
            suggestions['rationale'] = 'Portfolio is heavily concentrated. Rebalance to improve risk-adjusted returns.'
        
        return suggestions

class StockRecommendationEngine:
    """Generate stock recommendations based on multi-factor analysis"""
    
    @staticmethod
    def synthesize_recommendation(
        technical_signal: Dict,
        sentiment_data: Dict,
        fundamental_data: Dict,
        portfolio_context: Optional[Dict] = None
    ) -> Dict:
        """
        Synthesize multi-factor recommendation
        
        Args:
            technical_signal: From technical analyzer
            sentiment_data: From sentiment analyzer
            fundamental_data: Company fundamentals
            portfolio_context: User's portfolio info
            
        Returns:
            Dict with final recommendation, confidence, and reasoning
        """
        try:
            # Calculate weighted scores
            # Technical: 40% weight
            tech_score = 1 if technical_signal.get('signal') == 'BUY' else (
                -1 if technical_signal.get('signal') == 'SELL' else 0
            )
            tech_score *= technical_signal.get('confidence', 0.5)
            
            # Sentiment: 35% weight
            sentiment_score = 1 if sentiment_data.get('sentiment') == 'BULLISH' else (
                -1 if sentiment_data.get('sentiment') == 'BEARISH' else 0
            )
            
            # Fundamentals: 25% weight
            # Positive if PE is reasonable and growth is good
            pe_ratio = fundamental_data.get('pe_ratio', 'N/A')
            if isinstance(pe_ratio, (int, float)) and pe_ratio < 25:
                fundamental_score = 0.5
            else:
                fundamental_score = -0.2
            
            # Weighted average
            final_score = (
                tech_score * 0.4 +
                sentiment_score * 0.35 +
                fundamental_score * 0.25
            )
            
            # Generate recommendation
            if final_score > 0.3:
                recommendation = "BUY"
                confidence = min(0.95, 0.6 + final_score)
            elif final_score < -0.3:
                recommendation = "SELL"
                confidence = min(0.95, 0.6 - final_score)
            else:
                recommendation = "HOLD"
                confidence = 0.55
            
            # Build reasoning
            factors = []
            if technical_signal.get('signal') == 'BUY':
                factors.append(f"[BUY] Technical: {technical_signal.get('reasoning', 'Bullish pattern detected')}")
            elif technical_signal.get('signal') == 'SELL':
                factors.append(f"[SELL] Technical: {technical_signal.get('reasoning', 'Bearish pattern detected')}")
            
            if sentiment_data.get('sentiment') == 'BULLISH':
                factors.append(f"[BULLISH] Sentiment: {sentiment_data.get('sentiment')} based on recent news")
            elif sentiment_data.get('sentiment') == 'BEARISH':
                factors.append(f"[BEARISH] Sentiment: {sentiment_data.get('sentiment')} based on recent news")
            
            if isinstance(pe_ratio, (int, float)):
                factors.append(f"P/E Ratio: {pe_ratio:.1f}x (Market avg: ~20-25x)")
            
            # Portfolio context
            portfolio_note = ""
            if portfolio_context and portfolio_context.get('existing_concentration') and portfolio_context['existing_concentration'] > 5:
                portfolio_note = f"\n[WARNING] Note: Already {portfolio_context['existing_concentration']:.1f}% of portfolio. Concentration risk high."
                confidence *= 0.85  # Reduce confidence if already overweight
            
            return {
                'recommendation': recommendation,
                'confidence': confidence,
                'signal_score': final_score,
                'key_factors': factors,
                'portfolio_context': portfolio_note,
                'disclaimer': 'For informational purposes only. Not investment advice. Past performance ≠ future returns.'
            }
        except Exception as e:
            logger.error(f"Recommendation synthesis error: {str(e)}")
            return {
                'recommendation': 'HOLD',
                'confidence': 0.5,
                'key_factors': [],
                'disclaimer': 'Unable to generate recommendation due to insufficient data.'
            }
