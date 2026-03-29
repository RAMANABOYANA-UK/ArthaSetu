#!/usr/bin/env python
"""Interactive ArthaSetu Demo - Run on Your System"""

from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
from demo_data import SAMPLE_PORTFOLIO

print("\n" + "="*80)
print("ARTHSETU MARKET INTELLIGENCE - INTERACTIVE MODE")
print("="*80)
print("\nChoose an analysis:")
print("1. Analyze Stock (TCS)")
print("2. Analyze Stock (Infosys)")
print("3. Portfolio Risk Analysis")
print("4. Sector Rotation")
print("5. Exit")

orchestrator = SimpleMarketIntelligenceOrchestrator()

choice = input("\nEnter choice (1-5): ").strip()

if choice == '1':
    print("\n[ANALYZING] TCS Stock...")
    result = orchestrator.analyze_stock_for_buy('TCS')
    rec = result['recommendation']
    print(f"\n✓ Recommendation: {rec['recommendation']}")
    print(f"✓ Confidence: {rec['confidence']:.0%}")
    print(f"✓ Key Factors: {rec['key_factors']}")

elif choice == '2':
    print("\n[ANALYZING] Infosys Stock...")
    result = orchestrator.analyze_stock_for_buy('INFY')
    rec = result['recommendation']
    print(f"\n✓ Recommendation: {rec['recommendation']}")
    print(f"✓ Confidence: {rec['confidence']:.0%}")
    print(f"✓ Key Factors: {rec['key_factors']}")

elif choice == '3':
    print("\n[ANALYZING] Portfolio Risk...")
    result = orchestrator.analyze_portfolio_risk(SAMPLE_PORTFOLIO)
    if result['status'] == 'success':
        print(f"\n✓ Concentration Risk: {result['concentration']['concentration_risk']}")
        print(f"✓ Top Position: {result['top_positions'][0]['symbol']} ({result['top_positions'][0]['weight']:.1f}%)")

elif choice == '4':
    print("\n[ANALYZING] Sector Rotation...")
    result = orchestrator.analyze_sector_rotation()
    if result['status'] == 'success':
        print("\n✓ Ranked Sectors:")
        for i, (sector, data) in enumerate(result['ranked_sectors'].items(), 1):
            print(f"  {i}. {sector}: {data['sentiment']}")

elif choice == '5':
    print("\nGoodbye!")

else:
    print("Invalid choice!")

print("\n" + "="*80 + "\n")
