"""
Direct API Usage Examples for Market Intelligence Orchestrator
Judges can run these directly or import the orchestrator into their own scripts
"""

from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
from demo_data import SAMPLE_PORTFOLIO, DEMO_SCENARIOS
import json
import logging

# Configure logging to see agent workflow
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("=" * 80)
print("MARKET CHATGPT - NEXT GEN | Direct Python API Demo")
print("=" * 80)

# Initialize orchestrator
orchestrator = SimpleMarketIntelligenceOrchestrator()

# ============================================================================
# EXAMPLE 1: Stock Analysis - "Should I buy Infosys?"
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 1: Stock Analysis for Infosys")
print("=" * 80)

result = orchestrator.analyze_stock_for_buy("Infosys")

if result['status'] == 'success':
    print(f"\n✓ Analysis Complete for {result['symbol']}")
    print(f"  Ticker: {result['ticker']}")
    
    print("\n--- AGENT WORKFLOW ---")
    for step in result['agent_trajectory']:
        print(f"  {step}")
    
    print("\n--- LIVE PRICE DATA ---")
    if result['live_price']:
        price = result['live_price']
        print(f"  Current Price: ₹{price['current_price']:.2f}")
        print(f"  P/E Ratio: {price['pe_ratio']}")
        print(f"  Market Cap: {price['market_cap']}")
        print(f"  52-Week High: {price['fifty_two_week_high']}")
    
    print("\n--- TECHNICAL ANALYSIS ---")
    tech = result['technical_signal']
    print(f"  Signal: {tech['signal']}")
    print(f"  RSI: {tech['rsi']:.0f}")
    print(f"  Confidence: {tech['confidence']:.0%}")
    print(f"  Reasoning: {tech['reasoning']}")
    
    if result['divergence']['divergence_type'] != 'NONE':
        print(f"  ⚡ Divergence: {result['divergence']['divergence_type']}")
    
    print("\n--- SENTIMENT ANALYSIS ---")
    sentiment = result['sentiment']
    print(f"  Sentiment: {sentiment['sentiment']}")
    print(f"  Score: {sentiment['score']:.2f}")
    print(f"  Articles Analyzed: {sentiment['articles_analyzed']}")
    
    print("\n--- FINAL RECOMMENDATION ---")
    rec = result['recommendation']
    print(f"  Recommendation: {rec['recommendation']}")
    print(f"  Confidence: {rec['confidence']:.0%}")
    print(f"  Key Factors:")
    for factor in rec['key_factors']:
        print(f"    - {factor}")
    print(f"\n  ⚠️  {rec['disclaimer']}")
else:
    print(f"✗ Error: {result.get('message', 'Unknown error')}")

# ============================================================================
# EXAMPLE 2: Portfolio Risk Analysis
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 2: Portfolio Risk Audit")
print("=" * 80)

portfolio_result = orchestrator.analyze_portfolio_risk(SAMPLE_PORTFOLIO)

if portfolio_result['status'] == 'success':
    print(f"\n✓ Portfolio Analysis Complete")
    
    print("\n--- AGENT WORKFLOW ---")
    for step in portfolio_result['agent_trajectory']:
        print(f"  {step}")
    
    conc = portfolio_result['concentration']
    print(f"\n--- PORTFOLIO METRICS ---")
    print(f"  Total Value: ₹{conc.get('total_portfolio_value', 0):,.0f}")
    print(f"  Concentration Risk: {conc.get('concentration_risk', 'N/A')}")
    print(f"  Max Sector Weight: {conc.get('max_sector_weight', 0):.1f}%")
    
    print(f"\n--- SECTOR BREAKDOWN ---")
    for sector, weight in conc.get('sector_breakdown', {}).items():
        print(f"  {sector}: {weight:.1f}%")
    
    print(f"\n--- TOP 3 POSITIONS ---")
    for pos in conc.get('top_positions', [])[:3]:
        print(f"  {pos['symbol']}: {pos['weight']:.1f}% (₹{pos['value']:,.0f})")
    
    print(f"\n--- RECOMMENDATIONS ---")
    print(f"  {conc.get('recommendation', 'N/A')}")
    
    if portfolio_result['rebalance_suggestions']['reduce']:
        print(f"\n  Actions to Take:")
        for action in portfolio_result['rebalance_suggestions']['reduce']:
            print(f"    - Trim {action['symbol']} from {action['current_weight']:.1f}% to {action['target_weight']:.1f}%")
else:
    print(f"✗ Error: {portfolio_result.get('message', 'Unknown error')}")

# ============================================================================
# EXAMPLE 3: Sector Rotation Analysis
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 3: Sector Rotation Opportunity Analysis")
print("=" * 80)

sectors = ["IT", "Banking", "Pharma", "Auto", "FMCG"]
sector_result = orchestrator.analyze_sector_rotation(sectors)

if sector_result['status'] == 'success':
    print(f"\n✓ Sector Analysis Complete")
    
    print("\n--- AGENT WORKFLOW ---")
    for step in sector_result['agent_trajectory']:
        print(f"  {step}")
    
    print(f"\n--- SECTOR RANKINGS ---")
    for i, (sector, analysis) in enumerate(sector_result['ranked_sectors'], 1):
        print(f"  {i}. {sector}: {analysis['sentiment']}")
    
    print(f"\n--- RECOMMENDATION ---")
    print(f"  {sector_result['recommendation']}")
else:
    print(f"✗ Error: {sector_result.get('message', 'Unknown error')}")

# ============================================================================
# EXAMPLE 4: Custom Stock with Portfolio Context
# ============================================================================
print("\n" + "=" * 80)
print("EXAMPLE 4: Stock Analysis with Portfolio Context")
print("=" * 80)

# Get current Reliance position from sample portfolio
reliance_position = next((p for p in SAMPLE_PORTFOLIO if p['symbol'] == 'Reliance'), None)

if reliance_position:
    portfolio_context = {
        'concentration': (reliance_position['quantity'] * reliance_position['current_price']) / 100000 * 100  # % of portfolio
    }
    
    result = orchestrator.analyze_stock_for_buy("Reliance", portfolio_context)
    
    if result['status'] == 'success':
        print(f"\n✓ Context-Aware Analysis for {result['symbol']}")
        
        rec = result['recommendation']
        print(f"  Recommendation: {rec['recommendation']}")
        print(f"  Confidence: {rec['confidence']:.0%}")
        
        if rec.get('portfolio_context'):
            print(f"\n  Portfolio Context:")
            print(f"  {rec['portfolio_context']}")
        
        print(f"\n  Key Factors:")
        for factor in rec['key_factors']:
            print(f"    - {factor}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 80)
print("API SUMMARY - How to Use the Orchestrator")
print("=" * 80)

print("""
The SimpleMarketIntelligenceOrchestrator provides three main methods:

1. analyze_stock_for_buy(symbol, portfolio_context=None)
   - Performs comprehensive stock analysis
   - Returns: Dict with recommendation, confidence, technical/sentiment/fundamental data
   
2. analyze_portfolio_risk(holdings)
   - Analyzes concentration and risk
   - Returns: Dict with concentration metrics and rebalancing suggestions
   
3. analyze_sector_rotation(sectors=None)
   - Analyzes sector momentum and rotation opportunities
   - Returns: Dict with sector rankings and recommendations

Example Usage:
   from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
   
   orchestrator = SimpleMarketIntelligenceOrchestrator()
   result = orchestrator.analyze_stock_for_buy("TCS")
   
   if result['status'] == 'success':
       recommendation = result['recommendation']
       print(f"Signal: {recommendation['recommendation']}")
       print(f"Confidence: {recommendation['confidence']:.0%}")
       print(f"Factors: {recommendation['key_factors']}")
""")

print("\n" + "=" * 80)
print("✅ Demo Complete - All Agent Workflows Working!")
print("=" * 80)
