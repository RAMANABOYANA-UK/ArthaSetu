# Market ChatGPT - Next Generation
## AI-Powered Multi-Agent Financial Intelligence for Retail Investors

Intelligent investment platform combining technical analysis, sentiment analysis, and portfolio risk assessment for Indian retail investors.

### Features

- **💬 Market ChatGPT**: Interactive AI agent answering stock and portfolio questions
- **🔍 Multi-Factor Analysis**: Technical + Sentiment + Fundamentals synthesis
- **📊 Portfolio Audit**: Concentration risk analysis and rebalancing suggestions
- **🎯 Real-Time Alerts**: NSE stock data, news sentiment, technical signals
- **📈 India-Specific Insights**: FII/DII flows, sector rotation, currency impact

### Quick Start

#### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 2. Set Up Environment Variables
Create a `.env` file:
```
OPENAI_API_KEY=your_key_here
NEWSAPI_KEY=your_key_here  # Optional for demo
```

#### 3. Run the App
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

### Usage Modes

1. **Market Chat**: Ask questions like "Should I buy Infosys?" or "Is my portfolio overconcentrated?"
2. **Stock Analysis**: Deep dive into technical, sentiment, and fundamental analysis
3. **Portfolio Audit**: Get concentration risk assessment and rebalancing suggestions
4. **Demo Scenarios**: Try pre-built scenarios (Technical Analysis, Sentiment Analysis, Portfolio Risk)

### Architecture

**Multi-Agent System** (CrewAI):
- Market Data Researcher: Fetches real-time prices, fundamentals
- Technical Analyst: Detects patterns, divergences, support/resistance
- Sentiment Analyst: Processes news, earnings, institutional flows
- Portfolio Strategist: Synthesizes recommendations, assesses risk

**Data Sources**:
- yfinance: Stock prices, OHLCV data
- NewsAPI: Financial news and articles
- CoinGecko: Cryptocurrency data
- Technical Indicators: RSI, MACD, Moving Averages, Bollinger Bands

### Demo Portfolio

Sample portfolio with 6 stocks across IT, Banking, FMCG, Energy sectors. Load via sidebar to test analysis features.

### Key Features Demonstrated

✅ Real-time stock price data  
✅ Multi-timeframe technical analysis  
✅ News sentiment scoring (VADER)  
✅ Portfolio concentration metrics  
✅ Buy/Sell/Hold recommendations with confidence scores  
✅ Source attribution and agent reasoning transparency  
✅ India-specific market context  

### Limitations & Next Steps

**MVP Scope**:
- Session-based portfolio (no persistence)
- Limited to yfinance data (NSE mapping)
- Mock FII flows and sector rotation data
- Single LLM model (GPT-3.5-turbo)

**Post-Hackathon Enhancements**:
- Real-time NSE WebSocket integration
- User authentication + portfolio persistence
- Advanced MF analysis
- Scheduled alerts/newsletters
- Video generation (AI Market Video Engine)
- Historical backtesting framework

### Testing

Sample stocks available for testing:
- TCS
- Infosys
- Reliance
- HDFC Bank
- Wipro
- ITC

### License
Open source - MIT

### Support
For issues or questions, refer to the analysis explanations in-app or review agent reasoning traces.
