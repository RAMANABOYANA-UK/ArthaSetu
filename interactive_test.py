#!/usr/bin/env python3
"""
Interactive ArthaSetu API Tester
Test the market intelligence system with your own stock symbols and scenarios
"""

from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
import json

def print_result(result, title="Result"):
    """Pretty print API results"""
    print("\n" + "="*80)
    print(f"{title}")
    print("="*80)
    print(json.dumps(result, indent=2, default=str))
    print()

def main():
    print("\n" + "="*80)
    print("ARTHASETU - INTERACTIVE API TESTER")
    print("="*80)
    
    orchest = SimpleMarketIntelligenceOrchestrator()
    
    while True:
        print("\nOptions:")
        print("  1. Analyze stock for buy/sell (e.g., TCS, INFY, RELIANCE)")
        print("  2. Analyze portfolio risk")
        print("  3. Analyze sector rotation")
        print("  4. Exit")
        
        choice = input("\nEnter choice (1-4): ").strip()
        
        if choice == '1':
            symbol = input("Enter stock symbol (e.g., TCS): ").strip().upper()
            if symbol:
                print(f"\n[ANALYZING] {symbol}...")
                result = orchest.analyze_stock_for_buy(symbol)
                print_result(result, f"Stock Analysis: {symbol}")
                
                if result['status'] == 'success':
                    print("\n--- SUMMARY ---")
                    print(f"Recommendation: {result['recommendation']['recommendation']}")
                    print(f"Confidence: {result['recommendation']['confidence']:.0%}")
                    print(f"Sentiment: {result['sentiment']['sentiment']}")
        
        elif choice == '2':
            from demo_data import SAMPLE_PORTFOLIO
            print(f"\n[ANALYZING] Portfolio with {len(SAMPLE_PORTFOLIO)} holdings...")
            result = orchest.analyze_portfolio_risk(SAMPLE_PORTFOLIO)
            print_result(result, "Portfolio Risk Analysis")
            
            if result['status'] == 'success':
                print("\n--- SUMMARY ---")
                print(f"Total Value: {result['concentration']['total_value']:,.0f}")
                print(f"Concentration Risk: {result['concentration']['concentration_risk']}")
                print(f"Max Sector Weight: {result['concentration']['max_sector_weight']:.1f}%")
        
        elif choice == '3':
            sectors = ['IT', 'Banking', 'Pharma', 'Energy']
            print(f"\n[ANALYZING] Sectors: {', '.join(sectors)}...")
            result = orchest.analyze_sector_rotation(sectors)
            print_result(result, "Sector Rotation Analysis")
            
            if result['status'] == 'success':
                print("\n--- SECTOR RANKINGS ---")
                for sector, analysis in result['sector_analysis'].items():
                    print(f"  {sector}: {analysis['sentiment']}")
        
        elif choice == '4':
            print("\nExiting... Thanks for using ArthaSetu!")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
