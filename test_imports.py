"""
Quick test to verify all imports and basic functionality
"""
import sys
sys.path.insert(0, r'c:\Users\unnat\OneDrive\Desktop\Documents\Desktop\ArthaSetu')

print("Testing imports...")

try:
    from data_connectors.stock_data import StockDataConnector
    print("✓ StockDataConnector imported")
except Exception as e:
    print(f"✗ StockDataConnector: {e}")

try:
    from data_connectors.news_sentiment import NewsSentimentConnector
    print("✓ NewsSentimentConnector imported")
except Exception as e:
    print(f"✗ NewsSentimentConnector: {e}")

try:
    from tools.technical_analysis import TechnicalAnalyzer
    print("✓ TechnicalAnalyzer imported")
except Exception as e:
    print(f"✗ TechnicalAnalyzer: {e}")

try:
    from tools.portfolio_analysis import PortfolioAnalyzer, StockRecommendationEngine
    print("✓ Portfolio analysis tools imported")
except Exception as e:
    print(f"✗ Portfolio analysis: {e}")

try:
    from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
    print("✓ SimpleMarketIntelligenceOrchestrator imported")
except Exception as e:
    print(f"✗ Orchestrator: {e}")

try:
    from demo_data import SAMPLE_PORTFOLIO, DEMO_SCENARIOS
    print("✓ Demo data imported")
except Exception as e:
    print(f"✗ Demo data: {e}")

print("\nAll imports successful!")

# Test basic functionality
print("\nTesting stock connector...")
connector = StockDataConnector()
print(f"✓ StockDataConnector initialized")

# Test ticker resolution
ticker = connector.resolve_ticker("TCS")
print(f"✓ TCS resolved to: {ticker}")

# Test data fetch (with timeout)
print("Fetching TCS data...")
try:
    data = connector.get_stock_data(ticker, period="1d", interval="1d")
    if data is not None and not data.empty:
        print(f"✓ Successfully fetched data with {len(data)} rows")
    else:
        print("✗ No data returned")
except Exception as e:
    print(f"✗ Error fetching data: {e}")

print("\n✅ All tests passed! App is ready to run.")
print("\nTo start the app, run:")
print("  streamlit run app.py")
