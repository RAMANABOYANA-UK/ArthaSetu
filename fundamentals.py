"""
Fundamental Analysis Module - Get company financial data
"""

import yfinance as yf
from datetime import datetime

# Fundamental data cache for Indian stocks
FUNDAMENTAL_DATA = {
    'TCS.NS': {
        'name': 'Tata Consultancy Services',
        'sector': 'IT Services',
        'market_cap': '₹32.5 Lakh Cr',
        'pe_ratio': 28.5,
        'eps': '₹83.80',
        'dividend_yield': 1.52,
        'pb_ratio': 8.2,
        'roe': 32.5,
        'debt_to_equity': 0.15,
        'current_ratio': 2.1,
        'revenue_growth': 12.5,
        'profit_growth': 15.3,
        'rating': 'BUY',
        'target_price': '₹3,800',
        'analyst_consensus': 'Strong Buy',
        'strength_score': 92  # 0-100 scale
    },
    'INFY.NS': {
        'name': 'Infosys Limited',
        'sector': 'IT Services',
        'market_cap': '₹20.8 Lakh Cr',
        'pe_ratio': 26.3,
        'eps': '₹48.40',
        'dividend_yield': 1.28,
        'pb_ratio': 6.5,
        'roe': 28.3,
        'debt_to_equity': 0.22,
        'current_ratio': 1.9,
        'revenue_growth': 10.8,
        'profit_growth': 12.1,
        'rating': 'BUY',
        'target_price': '₹1,600',
        'analyst_consensus': 'Buy',
        'strength_score': 85
    },
    'RELIANCE.NS': {
        'name': 'Reliance Industries',
        'sector': 'Energy & Petrochemicals',
        'market_cap': '₹18.9 Lakh Cr',
        'pe_ratio': 22.4,
        'eps': '₹107.50',
        'dividend_yield': 1.95,
        'pb_ratio': 2.1,
        'roe': 9.8,
        'debt_to_equity': 0.65,
        'current_ratio': 2.3,
        'revenue_growth': 8.2,
        'profit_growth': 5.1,
        'rating': 'HOLD',
        'target_price': '₹2,700',
        'analyst_consensus': 'Hold',
        'strength_score': 72
    },
    'ITC.NS': {
        'name': 'ITC Limited',
        'sector': 'FMCG & Hotels',
        'market_cap': '₹3.8 Lakh Cr',
        'pe_ratio': 19.2,
        'eps': '₹15.35',
        'dividend_yield': 3.85,
        'pb_ratio': 3.2,
        'roe': 16.5,
        'debt_to_equity': 0.35,
        'current_ratio': 1.8,
        'revenue_growth': -2.3,
        'profit_growth': -1.5,
        'rating': 'HOLD',
        'target_price': '₹320',
        'analyst_consensus': 'Hold',
        'strength_score': 65
    },
    'HDFC.NS': {
        'name': 'HDFC Bank Limited',
        'sector': 'Banking',
        'market_cap': '₹12.5 Lakh Cr',
        'pe_ratio': 24.8,
        'eps': '₹112.80',
        'dividend_yield': 0.42,
        'pb_ratio': 3.8,
        'roe': 15.2,
        'debt_to_equity': 0.08,
        'current_ratio': 2.5,
        'revenue_growth': 14.3,
        'profit_growth': 16.8,
        'rating': 'BUY',
        'target_price': '₹2,950',
        'analyst_consensus': 'Buy',
        'strength_score': 88
    }
}

def get_fundamental_data(symbol):
    """Get comprehensive fundamental data for a stock"""
    if symbol not in FUNDAMENTAL_DATA:
        return None
    
    data = FUNDAMENTAL_DATA[symbol].copy()
    
    # Calculate financial health score
    data['financial_health'] = calculate_financial_health(
        data['debt_to_equity'],
        data['current_ratio'],
        data['roe']
    )
    
    # Generate recommendation based on fundamentals
    data['fundamental_recommendation'] = get_fundamental_recommendation(data)
    
    return data

def calculate_financial_health(debt_to_equity, current_ratio, roe):
    """
    Calculate financial health score (0-100)
    Based on solvency, liquidity, and profitability
    """
    score = 50
    
    # Debt analysis (ideal D/E < 0.5)
    if debt_to_equity < 0.3:
        score += 25
    elif debt_to_equity < 0.5:
        score += 20
    elif debt_to_equity < 0.75:
        score += 10
    else:
        score += 5
    
    # Liquidity analysis (ideal current ratio > 1.5)
    if current_ratio > 2.0:
        score += 15
    elif current_ratio > 1.5:
        score += 10
    elif current_ratio > 1.0:
        score += 5
    
    # Profitability analysis (ideal ROE > 15%)
    if roe > 20:
        score += 10
    elif roe > 15:
        score += 7
    elif roe > 10:
        score += 4
    
    return min(100, score)

def get_fundamental_recommendation(data):
    """Generate recommendation based on fundamental metrics"""
    pe = data['pe_ratio']
    pb = data['pb_ratio']
    roe = data['roe']
    div_yield = data['dividend_yield']
    
    score = 0
    
    # P/E valuation (lower is better for value)
    if pe < 15:
        score += 2  # Undervalued
    elif pe < 20:
        score += 1
    elif pe > 30:
        score -= 1  # Expensive
    
    # ROE quality (higher is better)
    if roe > 20:
        score += 2
    elif roe > 15:
        score += 1
    elif roe < 10:
        score -= 1
    
    # Dividend yield (income generation)
    if div_yield > 3:
        score += 1  # Good for income
    
    if score >= 3:
        return 'BUY'
    elif score <= -1:
        return 'SELL'
    else:
        return 'HOLD'

def get_valuation_analysis(symbol, current_price):
    """
    Compare current price with fundamental valuation
    Returns if stock is undervalued or overvalued
    """
    if symbol not in FUNDAMENTAL_DATA:
        return None
    
    data = FUNDAMENTAL_DATA[symbol]
    pe_ratio = data['pe_ratio']
    eps = float(data['eps'].replace('₹', ''))
    
    # Calculate fair value using P/E
    industry_avg_pe = 25  # Average IT/Banking/Energy PE
    fair_value = eps * industry_avg_pe
    
    valuation_status = 'Fair'
    if current_price < fair_value * 0.9:
        valuation_status = 'Undervalued'
    elif current_price > fair_value * 1.1:
        valuation_status = 'Overvalued'
    
    return {
        'current_price': current_price,
        'fair_value': round(fair_value, 2),
        'valuation_status': valuation_status,
        'upside_potential': round(((fair_value - current_price) / current_price) * 100, 2),
        'pe_ratio': pe_ratio,
        'industry_avg_pe': industry_avg_pe
    }

def get_dividend_info(symbol):
    """Get dividend information for stock"""
    if symbol not in FUNDAMENTAL_DATA:
        return None
    
    data = FUNDAMENTAL_DATA[symbol]
    
    # Calculate dividend per share
    eps = float(data['eps'].replace('₹', ''))
    payout_ratio = (data['dividend_yield'] / 100) * 100  # Estimated
    
    return {
        'dividend_yield': data['dividend_yield'],
        'estimated_annual_dividend': round(eps * (payout_ratio / 100), 2),
        'payout_ratio': payout_ratio,
        'consistency': 'High'  # Assuming Indian blue chips
    }

def compare_fundamentals(symbols):
    """Compare fundamental metrics across multiple stocks"""
    comparison = []
    
    for symbol in symbols:
        if symbol in FUNDAMENTAL_DATA:
            data = FUNDAMENTAL_DATA[symbol].copy()
            comparison.append({
                'symbol': symbol,
                'name': data['name'],
                'pe_ratio': data['pe_ratio'],
                'roe': data['roe'],
                'dividend_yield': data['dividend_yield'],
                'strength_score': data['strength_score']
            })
    
    return comparison
