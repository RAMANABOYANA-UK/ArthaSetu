"""
Risk Management Module
Portfolio risk analysis, position sizing, stop-loss recommendations
"""

def calculate_portfolio_risk(portfolio_items, prices):
    """
    Calculate overall portfolio risk and diversification
    Returns risk score (0-100), where higher = riskier
    """
    if not portfolio_items:
        return {}
    
    # Calculate portfolio allocation
    total_value = 0
    allocations = {}
    
    for item in portfolio_items:
        symbol = item['symbol']
        quantity = item['quantity']
        current_price = prices.get(symbol, 2500)  # Default mock
        
        value = quantity * current_price
        total_value += value
        allocations[symbol] = value
    
    if total_value == 0:
        return {}
    
    # Calculate concentration risk (Herfindahl index)
    concentration_risk = 0
    for symbol, value in allocations.items():
        weight = value / total_value
        concentration_risk += weight ** 2
    
    # Normalize to 0-100
    concentration_score = (concentration_risk - (1/len(allocations))) / (1 - (1/len(allocations))) * 100 if len(allocations) > 1 else 100
    concentration_score = max(0, min(100, concentration_score))
    
    # Diversification score (inverse of concentration)
    diversification_score = 100 - concentration_score
    
    return {
        'total_portfolio_value': round(total_value, 2),
        'diversification_score': round(diversification_score, 2),
        'concentration_risk': 'HIGH' if concentration_score > 70 else ('MEDIUM' if concentration_score > 40 else 'LOW'),
        'allocation_breakdown': {k: round(v/total_value * 100, 2) for k, v in allocations.items()},
        'largest_position': max(allocations.items(), key=lambda x: x[1])[0] if allocations else None,
        'largest_position_weight': round(max(allocations.values()) / total_value * 100, 2) if allocations else 0
    }

def calculate_position_size(account_balance, risk_percentage=2):
    """
    Calculate recommended position size based on account balance
    Typical risk management: Risk 1-2% of capital per trade
    """
    return {
        'account_balance': account_balance,
        'risk_per_trade_1pct': round(account_balance * 0.01, 2),
        'risk_per_trade_2pct': round(account_balance * 0.02, 2),
        'max_position_size_1pct': round(account_balance * 0.05, 2),  # 5x leverage for 1% risk
        'max_position_size_2pct': round(account_balance * 0.10, 2),  # 5x leverage for 2% risk
        'recommendation': 'Risk 1-2% per trade for sustainable growth'
    }

def calculate_stop_loss(entry_price, stop_loss_pct=5):
    """
    Calculate stop-loss levels for a position
    """
    sl_price = entry_price * (1 - stop_loss_pct / 100)
    tp_price = entry_price * (1 + stop_loss_pct * 2 / 100)  # 2:1 risk/reward
    
    return {
        'entry_price': round(entry_price, 2),
        'stop_loss_price': round(sl_price, 2),
        'take_profit_price': round(tp_price, 2),
        'risk_amount': round(entry_price - sl_price, 2),
        'profit_potential': round(tp_price - entry_price, 2),
        'risk_reward_ratio': '1:2'
    }

def calculate_var_value_at_risk(portfolio_value, daily_volatility=2, confidence_level=95):
    """
    Calculate Value at Risk (VaR)
    Shows potential maximum loss at given confidence level
    """
    # Simplified VaR calculation
    # VaR = Portfolio Value * Z-score * Daily Volatility
    
    z_scores = {95: 1.645, 99: 2.326}
    z_score = z_scores.get(confidence_level, 1.645)
    
    var = portfolio_value * z_score * (daily_volatility / 100)
    
    return {
        'portfolio_value': round(portfolio_value, 2),
        'daily_volatility': daily_volatility,
        'confidence_level': confidence_level,
        'max_expected_loss': round(var, 2),
        'loss_percentage': round((var / portfolio_value) * 100, 2),
        'interpretation': f'With {confidence_level}% confidence, max daily loss is ₹{round(var, 0)}'
    }

def calculate_sharpe_ratio(average_return, risk_free_rate=6.5, volatility=15):
    """
    Calculate Sharpe Ratio for risk-adjusted returns
    Sharpe Ratio = (Return - Risk-free rate) / Volatility
    Higher is better (>1 is good, >2 is excellent)
    """
    excess_return = average_return - risk_free_rate
    sharpe_ratio = excess_return / volatility if volatility > 0 else 0
    
    return {
        'average_return': average_return,
        'risk_free_rate': risk_free_rate,
        'volatility': volatility,
        'sharpe_ratio': round(sharpe_ratio, 3),
        'quality': 'Excellent' if sharpe_ratio > 2 else ('Good' if sharpe_ratio > 1 else 'Below Average'),
        'interpretation': 'Risk-adjusted return ratio. Use to compare investments with different risk levels.'
    }

def get_risk_rating(portfolio_items, prices, account_balance=100000):
    """
    Get comprehensive risk rating for portfolio
    Returns overall risk assessment and recommendations
    """
    portfolio_risk = calculate_portfolio_risk(portfolio_items, prices)
    
    if not portfolio_risk:
        return {}
    
    diversification_score = portfolio_risk.get('diversification_score', 50)
    
    # Determine risk profile
    if diversification_score > 80:
        risk_profile = 'CONSERVATIVE'
        risk_level = 'Low'
    elif diversification_score > 60:
        risk_profile = 'MODERATE'
        risk_level = 'Medium'
    elif diversification_score > 40:
        risk_profile = 'AGGRESSIVE'
        risk_level = 'High'
    else:
        risk_profile = 'VERY_AGGRESSIVE'
        risk_level = 'Very High'
    
    # Generate recommendations
    recommendations = []
    
    if diversification_score < 50:
        recommendations.append('Add more stocks to reduce concentration risk')
    
    largest_weight = portfolio_risk.get('largest_position_weight', 0)
    if largest_weight > 40:
        recommendations.append(f'Reduce {portfolio_risk["largest_position"]} position to <30% of portfolio')
    
    if len(portfolio_items) < 3:
        recommendations.append('Consider adding at least 3-5 stocks for better diversification')
    
    position_sizing = calculate_position_size(account_balance, 2)
    
    return {
        'risk_profile': risk_profile,
        'overall_risk_level': risk_level,
        'diversification_score': portfolio_risk.get('diversification_score'),
        'concentration_risk': portfolio_risk.get('concentration_risk'),
        'largest_position': f"{portfolio_risk.get('largest_position')} ({portfolio_risk.get('largest_position_weight')}%)",
        'var_daily': calculate_var_value_at_risk(portfolio_risk.get('total_portfolio_value'))['max_expected_loss'],
        'recommended_stop_loss': '5-7%',
        'recommended_position_size': position_sizing['risk_per_trade_2pct'],
        'recommendations': recommendations[:3]  # Top 3 recommendations
    }

def calculate_max_drawdown_protection(entry_price, max_loss_allowed_pct=10):
    """
    Calculate maximum drawdown and recovery requirements
    """
    max_allowed_loss = entry_price * (max_loss_allowed_pct / 100)
    drawdown_price = entry_price - max_allowed_loss
    
    # To recover from drawdown, gain % required is higher than loss %
    recovery_pct_needed = (entry_price - drawdown_price) / drawdown_price * 100
    
    return {
        'entry_price': round(entry_price, 2),
        'max_drawdown_allowed': round(max_allowed_loss, 2),
        'drawdown_price': round(drawdown_price, 2),
        'drawdown_percentage': max_loss_allowed_pct,
        'recovery_needed': round(recovery_pct_needed, 2),
        'interpretation': f'To recover from {max_loss_allowed_pct}% loss, gain of {round(recovery_pct_needed, 2)}% needed'
    }
