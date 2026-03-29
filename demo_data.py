"""
Sample portfolio for demo purposes
"""

SAMPLE_PORTFOLIO = [
    {
        "symbol": "TCS",
        "company_name": "Tata Consultancy Services",
        "sector": "IT",
        "quantity": 10,
        "entry_price": 3500,
        "current_price": 3650,
        "return_pct": 4.29
    },
    {
        "symbol": "Infosys",
        "company_name": "Infosys Limited",
        "sector": "IT",
        "quantity": 15,
        "entry_price": 1500,
        "current_price": 1580,
        "return_pct": 5.33
    },
    {
        "symbol": "Reliance",
        "company_name": "Reliance Industries",
        "sector": "Energy",
        "quantity": 20,
        "entry_price": 2400,
        "current_price": 2350,
        "return_pct": -2.08
    },
    {
        "symbol": "HDFCBANK",
        "company_name": "HDFC Bank",
        "sector": "Banking",
        "quantity": 5,
        "entry_price": 1800,
        "current_price": 1850,
        "return_pct": 2.78
    },
    {
        "symbol": "Wipro",
        "company_name": "Wipro Limited",
        "sector": "IT",
        "quantity": 20,
        "entry_price": 420,
        "current_price": 445,
        "return_pct": 5.95
    },
    {
        "symbol": "ITC",
        "company_name": "ITC Limited",
        "sector": "FMCG",
        "quantity": 100,
        "entry_price": 320,
        "current_price": 345,
        "return_pct": 7.81
    }
]

DEMO_SCENARIOS = {
    "scenario_a": {
        "title": "Should I Buy Infosys? (Technical Analysis Focus)",
        "query": "Is Infosys showing a buy signal based on technical analysis?",
        "symbol": "Infosys",
        "context": "Stock has dipped 8% in last month. Checking if it's a good entry point for long-term investment."
    },
    "scenario_b": {
        "title": "Hold or Sell Reliance Post Q3? (Sentiment Focus)",
        "query": "Should I hold my Reliance position given the recent quarterly results and market sentiment?",
        "symbol": "Reliance",
        "portfolio_context": [p for p in SAMPLE_PORTFOLIO if p['symbol'] == 'Reliance'],
        "context": "Recently reported Q3 results. Need to assess if position should be trimmed."
    },
    "scenario_c": {
        "title": "Portfolio Risk Audit (Concentration Analysis)",
        "query": "Analyze my portfolio for concentration risk and suggest rebalancing moves.",
        "portfolio": SAMPLE_PORTFOLIO,
        "context": "Want to understand my portfolio's risk profile and get rebalancing suggestions."
    }
}
