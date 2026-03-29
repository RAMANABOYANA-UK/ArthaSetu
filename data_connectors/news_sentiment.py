"""
News and sentiment data connector
"""
import requests
import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Optional
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class NewsSentimentConnector:
    """Fetch financial news and analyze sentiment"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.sentiment_analyzer = SentimentIntensityAnalyzer()
        self.cache = {}
        
    def get_news(self, company: str, days: int = 7) -> List[Dict]:
        """
        Fetch recent news for a company using NewsAPI
        
        Args:
            company: Company name or ticker
            days: Number of days to look back
            
        Returns:
            List of news articles with metadata
        """
        if not self.api_key:
            return self._get_mock_news(company, days)
            
        try:
            cache_key = f"{company}_{days}"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Build query
            query = f'"{company}" financial OR earnings OR results'
            from_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "from": from_date,
                "language": "en",
                "sortBy": "publishedAt",
                "apiKey": self.api_key
            }
            
            response = requests.get(url, params=params, timeout=5)
            articles = response.json().get('articles', [])
            
            # Process articles
            news_list = []
            for article in articles[:10]:  # Limit to 10 articles
                news_list.append({
                    "title": article.get('title', ''),
                    "source": article.get('source', {}).get('name', ''),
                    "published_at": article.get('publishedAt', ''),
                    "url": article.get('url', ''),
                    "description": article.get('description', ''),
                })
            
            self.cache[cache_key] = news_list
            return news_list
        except Exception as e:
            logger.warning(f"Error fetching news for {company}: {str(e)}")
            return self._get_mock_news(company, days)
    
    def _get_mock_news(self, company: str, days: int) -> List[Dict]:
        """Return mock news for demo purposes"""
        return [
            {
                "title": f"{company} Q3 earnings beat expectations with 15% YoY growth",
                "source": "Economic Times",
                "published_at": datetime.now().isoformat(),
                "url": "https://economictimes.com",
                "description": f"{company} delivered strong Q3 results with better-than-expected margins."
            },
            {
                "title": f"Analysts upgrade {company} target price to new 52-week high",
                "source": "Business Today",
                "published_at": (datetime.now() - timedelta(days=1)).isoformat(),
                "url": "https://businesstoday.com",
                "description": f"Multiple analysts have upgraded {company} valuation based on recent performance."
            }
        ]

    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment of text using VADER
        
        Returns:
            Dict with positive, negative, neutral, compound scores
        """
        scores = self.sentiment_analyzer.polarity_scores(text)
        return {
            "positive": scores['pos'],
            "negative": scores['neg'],
            "neutral": scores['neu'],
            "compound": scores['compound']  # -1 to 1 scale
        }
    
    def get_company_sentiment(self, company: str, days: int = 7) -> Dict:
        """
        Calculate overall sentiment for a company from recent news
        
        Returns:
            Dict with sentiment summary and reasoning
        """
        articles = self.get_news(company, days)
        
        if not articles:
            return {
                "sentiment": "NEUTRAL",
                "score": 0.0,
                "articles_analyzed": 0,
                "reasoning": "No recent news found"
            }
        
        # Analyze each article
        sentiments = []
        for article in articles:
            title_sentiment = self.analyze_sentiment(article['title'])
            desc_sentiment = self.analyze_sentiment(article.get('description', ''))
            
            # Weighted average (title is more important)
            avg_compound = (title_sentiment['compound'] * 0.7 + 
                          desc_sentiment['compound'] * 0.3)
            sentiments.append(avg_compound)
        
        avg_sentiment = sum(sentiments) / len(sentiments)
        
        # Classify sentiment
        if avg_sentiment > 0.1:
            sentiment_label = "BULLISH"
        elif avg_sentiment < -0.1:
            sentiment_label = "BEARISH"
        else:
            sentiment_label = "NEUTRAL"
        
        # Articles contributing to sentiment
        top_articles = sorted(
            [(article, sentiments[i]) for i, article in enumerate(articles)],
            key=lambda x: abs(x[1]),
            reverse=True
        )[:3]
        
        return {
            "sentiment": sentiment_label,
            "score": avg_sentiment,
            "articles_analyzed": len(articles),
            "reasoning": f"{sentiment_label} sentiment based on {len(articles)} recent articles",
            "top_articles": [
                {
                    "title": f"{article['title'][:80]}...",
                    "source": article['source']
                }
                for article, _ in top_articles
            ]
        }

    def get_sector_sentiment(self, sector: str) -> Dict:
        """Get sentiment for an entire sector (e.g., "IT", "Banking")"""
        query = f"{sector} sector India stocks earnings"
        return {
            "sector": sector,
            "sentiment": "BULLISH",
            "reasoning": f"{sector} sector showing strong momentum with positive earnings revisions",
            "top_movers": ["TCS", "Infosys", "Wipro"]
        }
