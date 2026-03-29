"""
Direct Python API Demo - Market ChatGPT Next Gen
Simple version without unicode characters (for Windows compatibility)
"""

from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
from demo_data import SAMPLE_PORTFOLIO
import sys

# Suppress warnings
import warnings
warnings.filterwarnings('ignore')

orchestrator = SimpleMarketIntelligenceOrchestrator()

print("="*80)
print("MARKET CHATGPT - NEXT GEN | Direct Python API Demo")
print("="*80)

# ============================================================================
# EXAMPLE 1: Stock Analysis
# ============================================================================
print("\n" + "="*80)
print("EXAMPLE 1: Stock Analysis for Infosys")
print("="*80)

result = orchestrator.analyze_stock_for_buy("Infosys")

if result['status'] == 'success':
    print("\n[SUCCESS] Analysis Complete for", result['symbol'])
    print("  Ticker:", result['ticker'])
    
    print("\n--- AGENT WORKFLOW ---")
    for step in result['agent_trajectory']:
        print(" ", step)
    
    print("\n--- LIVE PRICE DATA ---")
    if result['live_price']:
        price = result['live_price']
        print(f"  Current Price: {price['current_price']:.2f}")
        print(f"  P/E Ratio: {price['pe_ratio']}")
        print(f"  Market Cap: {price['market_cap']}")
    
    print("\n--- TECHNICAL ANALYSIS ---")
    tech = result['technical_signal']
    print(f"  Signal: {tech['signal']}")
    print(f"  RSI: {tech['rsi']:.0f}")
    print(f"  Confidence: {tech['confidence']:.0%}")
    
    print("\n--- SENTIMENT ANALYSIS ---")
    sentiment = result['sentiment']
    print(f"  Sentiment: {sentiment['sentiment']}")
    print(f"  Score: {sentiment['score']:.2f}")
    
    print("\n--- FINAL RECOMMENDATION ---")
    rec = result['recommendation']
    print(f"  Recommendation: {rec['recommendation']}")
    print(f"  Confidence: {rec['confidence']:.0%}")
    print("  Key Factors:")
    for factor in rec['key_factors']:
        print(f"    - {factor}")
else:
    print("[ERROR]", result.get('message', 'Unknown error'))

# ============================================================================
# EXAMPLE 2: Portfolio Analysis
# ============================================================================
print("\n"+"="*80)
print("EXAMPLE 2: Portfolio Risk Audit")
print("="*80)

portfolio_result = orchestrator.analyze_portfolio_risk(SAMPLE_PORTFOLIO)

if portfolio_result['status'] == 'success':
    print("\n[SUCCESS] Portfolio Analysis Complete")
    
    print("\n--- AGENT WORKFLOW ---")
    for step in portfolio_result['agent_trajectory']:
        print(" ", step)
    
    conc = portfolio_result['concentration']
    print("\n--- PORTFOLIO METRICS ---")
    print(f"  Total Value: {conc.get('total_portfolio_value', 0):,.0f}")
    print(f"  Concentration Risk: {conc.get('concentration_risk', 'N/A')}")
    print(f"  Max Sector Weight: {conc.get('max_sector_weight', 0):.1f}%")
    
    print("\n--- SECTOR BREAKDOWN ---")
    for sector, weight in conc.get('sector_breakdown', {}).items():
        print(f"  {sector}: {weight:.1f}%")
    
    print("\n--- TOP 3 POSITIONS ---")
    for pos in conc.get('top_positions', [])[:3]:
        print(f"  {pos['symbol']}: {pos['weight']:.1f}%")
else:
    print("[ERROR]", portfolio_result.get('message', 'Unknown error'))

# ============================================================================
# EXAMPLE 3: Sector Rotation
# ============================================================================
print("\n"+"="*80)
print("EXAMPLE 3: Sector Rotation Analysis")
print("="*80)

sector_result = orchestrator.analyze_sector_rotation(['IT', 'Banking', 'Pharma'])

if sector_result['status'] == 'success':
    print("\n[SUCCESS] Sector Analysis Complete")
    
    print("\n--- AGENT WORKFLOW ---")
    for step in sector_result['agent_trajectory']:
        print(" ", step)
    
    print("\n--- SECTOR RANKINGS ---")
    for i, (sector, analysis) in enumerate(sector_result['ranked_sectors'], 1):
        print(f"  {i}. {sector}: {analysis['sentiment']}")
else:
    print("[ERROR]", sector_result.get('message', 'Unknown error'))

# ============================================================================
# API Usage Instructions
# ============================================================================
print("\n"+"="*80)
print("HOW TO USE THE API")
print("="*80)

print("""
The SimpleMarketIntelligenceOrchestrator provides 3 main methods:

1. analyze_stock_for_buy(symbol, portfolio_context=None)
   >> Returns BUY/SELL/HOLD recommendation with confidence
   
   Example:
       result = orchestrator.analyze_stock_for_buy("TCS")
       print(result['recommendation']['recommendation'])  # BUY/SELL/HOLD
       print(result['recommendation']['confidence'])       # % confidence

2. analyze_portfolio_risk(holdings)
   >> Returns concentration risk and rebalancing suggestions
   
   Example:
       holdings = [
           {'symbol': 'TCS', 'sector': 'IT', 'quantity': 10, 'current_price': 3650},
           {'symbol': 'INFY', 'sector': 'IT', 'quantity': 15, 'current_price': 1580},
       ]
       result = orchestrator.analyze_portfolio_risk(holdings)
       print(result['concentration']['concentration_risk'])  # LOW/MEDIUM/HIGH

3. analyze_sector_rotation(sectors=None)
   >> Returns sector momentum and rotation recommendations
   
   Example:
       result = orchestrator.analyze_sector_rotation(['IT', 'Banking'])
       for sector, analysis in result['sector_analysis'].items():
           print(f"{sector}: {analysis['sentiment']}")

All results include:
   - 'status': 'success' or 'error'
   - 'agent_trajectory': List of agent steps (shows multi-agent collaboration)
   - Detailed analysis data (technical, sentiment, fundamentals)
""")

print("="*80)
print("[SUCCESS] Demo complete - Ready for hackathon judges!")
print("="*80)
