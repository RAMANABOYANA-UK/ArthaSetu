"""
News & Sentiment Analysis Module
"""

from datetime import datetime, timedelta
import random

# Simulated market news for Indian stocks
MARKET_NEWS = {
    'TCS.NS': [
        {
            'headline': 'TCS Q4 FY2026 Results: Revenue growth accelerates to 12.5% YoY',
            'source': 'BSE',
            'date': datetime.now() - timedelta(hours=2),
            'sentiment': 'POSITIVE',
            'impact': 'High',
            'summary': 'Tata Consultancy reported strong Q4 results with double-digit growth'
        },
        {
            'headline': 'TCS wins $150M digital transformation contract from global bank',
            'source': 'Business Today',
            'date': datetime.now() - timedelta(days=1),
            'sentiment': 'POSITIVE',
            'impact': 'Medium',
            'summary': 'New contract win signals strong demand for IT services'
        },
        {
            'headline': 'Global IT spending growth estimated at 8.2% driven by AI adoption',
            'source': 'Gartner',
            'date': datetime.now() - timedelta(days=2),
            'sentiment': 'POSITIVE',
            'impact': 'Medium',
            'summary': 'Sector tailwinds supporting IT service providers like TCS'
        }
    ],
    'INFY.NS': [
        {
            'headline': 'Infosys signs multi-year deal with Fortune 500 tech company',
            'source': 'Economic Times',
            'date': datetime.now() - timedelta(hours=5),
            'sentiment': 'POSITIVE',
            'impact': 'High',
            'summary': 'Major contract win validates Infosys 2026 growth strategy'
        },
        {
            'headline': 'Infosys to increase hiring for cloud and AI skills',
            'source': 'MoneyControl',
            'date': datetime.now() - timedelta(days=1),
            'sentiment': 'POSITIVE',
            'impact': 'Low',
            'summary': 'Expansion plans indicate revenue growth opportunities'
        }
    ],
    'RELIANCE.NS': [
        {
            'headline': 'Crude oil prices surge on geopolitical tensions',
            'source': 'Reuters',
            'date': datetime.now() - timedelta(hours=3),
            'sentiment': 'POSITIVE',
            'impact': 'High',
            'summary': 'Higher oil prices may benefit Reliance refining margins'
        },
        {
            'headline': 'RIL Q4 FY2026: Refining margins soften amid global demand concern',
            'source': 'BSE',
            'date': datetime.now() - timedelta(days=2),
            'sentiment': 'NEGATIVE',
            'impact': 'Medium',
            'summary': 'Margin pressure from weak global refining spreads'
        }
    ],
    'ITC.NS': [
        {
            'headline': 'FMCG sector faces consumer spending slowdown in rural markets',
            'source': 'Business Line',
            'date': datetime.now() - timedelta(hours=4),
            'sentiment': 'NEGATIVE',
            'impact': 'High',
            'summary': 'Rural demand weakness impacts ITC FMCG division'
        },
        {
            'headline': 'ITC Hotels division shows recovery with occupancy rates rising to 72%',
            'source': 'TradeIndia',
            'date': datetime.now() - timedelta(days=1),
            'sentiment': 'POSITIVE',
            'impact': 'Medium',
            'summary': 'Tourism recovery supporting hotel business upside'
        }
    ]
}

# Sentiment indicators from social media/analysts
SENTIMENT_SCORES = {
    'TCS.NS': {
        'social_media': 78,  # 0-100, positive slant
        'analyst_calls': 82,
        'retail_sentiment': 75,
        'institutional_sentiment': 85,
        'overall': 80  # Average
    },
    'INFY.NS': {
        'social_media': 72,
        'analyst_calls': 80,
        'retail_sentiment': 70,
        'institutional_sentiment': 82,
        'overall': 76
    },
    'RELIANCE.NS': {
        'social_media': 58,
        'analyst_calls': 62,
        'retail_sentiment': 60,
        'institutional_sentiment': 65,
        'overall': 61
    },
    'ITC.NS': {
        'social_media': 45,
        'analyst_calls': 52,
        'retail_sentiment': 48,
        'institutional_sentiment': 55,
        'overall': 50
    },
    'HDFC.NS': {
        'social_media': 70,
        'analyst_calls': 78,
        'retail_sentiment': 68,
        'institutional_sentiment': 80,
        'overall': 74
    }
}

def get_latest_news(symbol, limit=5):
    """Get latest news for a stock"""
    if symbol not in MARKET_NEWS:
        return []
    
    news_items = MARKET_NEWS[symbol][:limit]
    
    # Format dates
    formatted_news = []
    for item in news_items:
        formatted_news.append({
            'headline': item['headline'],
            'source': item['source'],
            'time_ago': format_time_ago(item['date']),
            'sentiment': item['sentiment'],
            'impact': item['impact'],
            'summary': item['summary']
        })
    
    return formatted_news

def get_sentiment_analysis(symbol):
    """Get comprehensive sentiment analysis"""
    if symbol not in SENTIMENT_SCORES:
        return None
    
    scores = SENTIMENT_SCORES[symbol]
    
    # Determine sentiment direction
    overall = scores['overall']
    if overall >= 70:
        sentiment_direction = 'BULLISH'
    elif overall >= 60:
        sentiment_direction = 'NEUTRAL_POSITIVE'
    elif overall >= 40:
        sentiment_direction = 'NEUTRAL'
    elif overall >= 30:
        sentiment_direction = 'NEUTRAL_NEGATIVE'
    else:
        sentiment_direction = 'BEARISH'
    
    return {
        'overall_sentiment': sentiment_direction,
        'sentiment_score': overall,
        'breakdown': {
            'social_media': scores['social_media'],
            'analyst_calls': scores['analyst_calls'],
            'retail_sentiment': scores['retail_sentiment'],
            'institutional_sentiment': scores['institutional_sentiment']
        },
        'trend': 'improving' if overall > 60 else 'declining',
        'confidence': round(abs(scores['analyst_calls'] - scores['social_media']) / 100, 2)  # Agreement level
    }

def get_news_sentiment_impact(symbol):
    """Analyze news impact on stock sentiment"""
    if symbol not in MARKET_NEWS:
        return {}
    
    news_items = MARKET_NEWS[symbol]
    
    positive_count = sum(1 for n in news_items if n['sentiment'] == 'POSITIVE')
    negative_count = sum(1 for n in news_items if n['sentiment'] == 'NEGATIVE')
    
    # Calculate recent impact (last 7 days)
    recent_news = [n for n in news_items if (datetime.now() - n['date']).days <= 7]
    high_impact = [n for n in recent_news if n['impact'] == 'High']
    
    sentiment_trend = 'IMPROVING' if positive_count > negative_count else 'DECLINING'
    
    return {
        'recent_positive_count': positive_count,
        'recent_negative_count': negative_count,
        'sentiment_trend': sentiment_trend,
        'high_impact_news': len(high_impact),
        'latest_news_summary': get_latest_news(symbol, 2)
    }

def format_time_ago(date):
    """Format datetime to 'X time ago' format"""
    now = datetime.now()
    diff = now - date
    
    if diff.seconds < 60:
        return f"{diff.seconds}s ago"
    elif diff.seconds < 3600:
        return f"{diff.seconds // 60}m ago"
    elif diff.seconds < 86400:
        return f"{diff.seconds // 3600}h ago"
    else:
        return f"{diff.days}d ago"

def get_news_impact_score(symbol):
    """
    Calculate impact score of recent news
    Returns how much news is affecting the stock (0-100)
    """
    if symbol not in MARKET_NEWS:
        return 0
    
    news_items = MARKET_NEWS[symbol]
    
    # Weight recent news more heavily
    impact_score = 0
    for item in news_items[:5]:  # Last 5 news
        days_old = (datetime.now() - item['date']).days
        
        # Fresh news gets more weight
        recency_weight = max(1, 5 - days_old)
        
        # Impact level weight
        impact_weight = {'High': 3, 'Medium': 2, 'Low': 1}[item['impact']]
        
        # Sentiment weight
        sentiment_weight = 1 if item['sentiment'] == 'POSITIVE' else -0.8
        
        impact_score += (recency_weight * impact_weight * sentiment_weight)
    
    # Normalize to 0-100
    impact_score = max(0, min(100, impact_score * 10))
    return round(impact_score, 2)

def compare_sentiments(symbols):
    """Compare sentiment across multiple stocks"""
    comparison = []
    
    for symbol in symbols:
        sentiment = get_sentiment_analysis(symbol)
        if sentiment:
            comparison.append({
                'symbol': symbol,
                'sentiment_score': sentiment['sentiment_score'],
                'trend': sentiment['trend'],
                'analyst_calls': sentiment['breakdown']['analyst_calls'],
                'retail_sentiment': sentiment['breakdown']['retail_sentiment']
            })
    
    return comparison
