"""
Quick reference API documentation for the orchestrator
"""

API_REFERENCE = """
╔════════════════════════════════════════════════════════════════════════╗
║           MARKET CHATGPT - NEXT GEN | API REFERENCE                   ║
║                     Direct Python Integration                         ║
╚════════════════════════════════════════════════════════════════════════╝

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. ORCHESTRATOR INITIALIZATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
    
    orchestrator = SimpleMarketIntelligenceOrchestrator()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
2. ANALYZE SINGLE STOCK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METHOD:
    orchestrator.analyze_stock_for_buy(
        symbol: str,
        portfolio_context: Optional[Dict] = None
    ) -> Dict

PARAMETERS:
    symbol: Stock name or ticker
            Examples: "TCS", "Infosys", "Reliance", "HDFC Bank"
    
    portfolio_context: Optional dict with existing holdings info
                      Example: {'existing_concentration': 5.2}

RETURNS: Dict with keys:
    - status: "success" or "error"
    - symbol: Stock symbol analyzed
    - ticker: Resolved yfinance ticker
    - live_price: Current price, P/E, market cap, etc.
    - technical_signal: {signal, confidence, rsi, reasoning}
    - sentiment: {sentiment, score, articles_analyzed}
    - fundamentals: {pe_ratio, sector, roe, debt_to_equity, ...}
    - recommendation: {recommendation, confidence, key_factors, disclaimer}
    - agent_trajectory: List of agent steps taken

EXAMPLE:
    result = orchestrator.analyze_stock_for_buy("TCS")
    
    if result['status'] == 'success':
        rec = result['recommendation']
        print(f"Signal: {rec['recommendation']}")  # BUY/SELL/HOLD
        print(f"Confidence: {rec['confidence']:.0%}")
        print(f"Factors: {rec['key_factors']}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
3. ANALYZE PORTFOLIO RISK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METHOD:
    orchestrator.analyze_portfolio_risk(holdings: List[Dict]) -> Dict

PARAMETERS:
    holdings: List of dicts with portfolio positions
             Format: [
                 {'symbol': 'TCS', 'sector': 'IT', 'quantity': 10, 'current_price': 3650},
                 {'symbol': 'INFY', 'sector': 'IT', 'quantity': 15, 'current_price': 1580},
                 ...
             ]

RETURNS: Dict with keys:
    - status: "success" or "error"
    - concentration: {total_value, concentration_risk, sector_breakdown, top_positions}
    - metrics: {volatility, sharpe_ratio, expected_return}
    - rebalance_suggestions: {reduce: [...], add: [...]}
    - agent_trajectory: List of agent steps

EXAMPLE:
    holdings = [
        {'symbol': 'TCS', 'sector': 'IT', 'quantity': 10, 'current_price': 3650},
        {'symbol': 'INFY', 'sector': 'IT', 'quantity': 15, 'current_price': 1580},
    ]
    
    result = orchestrator.analyze_portfolio_risk(holdings)
    
    if result['status'] == 'success':
        conc = result['concentration']
        print(f"Risk: {conc['concentration_risk']}")  # LOW/MEDIUM/HIGH
        print(f"Sectors: {conc['sector_breakdown']}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
4. ANALYZE SECTOR ROTATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

METHOD:
    orchestrator.analyze_sector_rotation(sectors: Optional[List[str]]) -> Dict

PARAMETERS:
    sectors: List of sector names (default: major Indian sectors)
            Default: ["IT", "Banking", "Pharma", "Auto", "FMCG", "Utilities"]

RETURNS: Dict with keys:
    - status: "success" or "error"
    - sector_analysis: {sector: sentiment_data, ...}
    - ranked_sectors: Sectors ranked by bullish/bearish sentiment
    - recommendation: Suggested rotation actions
    - agent_trajectory: List of agent steps

EXAMPLE:
    result = orchestrator.analyze_sector_rotation(["IT", "Banking", "Pharma"])
    
    if result['status'] == 'success':
        for sector, sentiment in result['sector_analysis'].items():
            print(f"{sector}: {sentiment['sentiment']}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
5. AGENT WORKFLOW VISIBILITY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Each result includes 'agent_trajectory' showing exactly what each agent did:

    result['agent_trajectory'] = [
        "✓ Market Data Researcher: Fetched live prices and fundamentals",
        "✓ Technical Analyst: Detected patterns and support/resistance",
        "✓ Sentiment Analyst: Processed recent news and market sentiment",
        "✓ Portfolio Strategist: Synthesized multi-factor recommendation"
    ]

This proves multi-agent collaboration and can be printed to show judges the workflow.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
6. DATA CONNECTORS (Direct Access)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Stock Data:
    from data_connectors.stock_data import StockDataConnector
    
    connector = StockDataConnector()
    data = connector.get_stock_data("TCS.NS", period="1y")
    price = connector.get_live_price("TCS.NS")
    fundamentals = connector.get_fundamental_data("TCS.NS")

News & Sentiment:
    from data_connectors.news_sentiment import NewsSentimentConnector
    
    news = NewsSentimentConnector()
    sentiment = news.get_company_sentiment("TCS")
    articles = news.get_news("TCS", days=7)

Technical Analysis:
    from tools.technical_analysis import TechnicalAnalyzer
    
    signal = TechnicalAnalyzer.get_technical_signal(data)
    rsi = TechnicalAnalyzer.calculate_rsi(data)
    macd = TechnicalAnalyzer.calculate_macd(data)

Portfolio Analysis:
    from tools.portfolio_analysis import PortfolioAnalyzer
    
    analysis = PortfolioAnalyzer.analyze_concentration(holdings)
    metrics = PortfolioAnalyzer.calculate_portfolio_metrics(holdings)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
7. SAMPLE PORTFOLIO & SCENARIOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Pre-configured data for quick testing:
    from demo_data import SAMPLE_PORTFOLIO, DEMO_SCENARIOS
    
    # Use sample portfolio
    result = orchestrator.analyze_portfolio_risk(SAMPLE_PORTFOLIO)
    
    # Access demo scenarios
    scenario_a = DEMO_SCENARIOS['scenario_a']
    print(scenario_a['title'])  # "Should I Buy Infosys? (Technical Analysis Focus)"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
8. COMPLETE EXAMPLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
    from demo_data import SAMPLE_PORTFOLIO
    
    # Initialize
    orchestrator = SimpleMarketIntelligenceOrchestrator()
    
    # Scenario 1: Analyze a stock
    print("\n=== STOCK ANALYSIS ===")
    result = orchestrator.analyze_stock_for_buy("Infosys")
    if result['status'] == 'success':
        print(f"Signal: {result['recommendation']['recommendation']}")
        print(f"Confidence: {result['recommendation']['confidence']:.0%}")
        print(f"Agents Used: {result['agent_trajectory']}")
    
    # Scenario 2: Portfolio audit
    print("\n=== PORTFOLIO AUDIT ===")
    portfolio_result = orchestrator.analyze_portfolio_risk(SAMPLE_PORTFOLIO)
    if portfolio_result['status'] == 'success':
        print(f"Risk Level: {portfolio_result['concentration']['concentration_risk']}")
        print(f"Sectors: {portfolio_result['concentration']['sector_breakdown']}")
    
    # Scenario 3: Sector rotation
    print("\n=== SECTOR ROTATION ===")
    sector_result = orchestrator.analyze_sector_rotation()
    if sector_result['status'] == 'success':
        for sector, analysis in sector_result['ranked_sectors'][:3]:
            print(f"  {sector}: {analysis['sentiment']}")

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
9. TESTING & RUNNING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Run the demo:
    python demo_usage.py

Import and test directly in Python:
    from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
    orch = SimpleMarketIntelligenceOrchestrator()
    result = orch.analyze_stock_for_buy("TCS")

Show to judges:
    - Explain the 4-agent architecture
    - Show agent_trajectory proving multi-agent collaboration
    - Display recommendation with confidence and reasoning
    - Show technical + sentiment + fundamentals synthesis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

if __name__ == "__main__":
    print(API_REFERENCE)
