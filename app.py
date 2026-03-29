"""
Streamlit frontend for Market Intelligence Agent
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import logging
from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
from demo_data import SAMPLE_PORTFOLIO, DEMO_SCENARIOS
from data_connectors.stock_data import StockDataConnector
from data_connectors.news_sentiment import NewsSentimentConnector
from tools.technical_analysis import TechnicalAnalyzer
from tools.portfolio_analysis import PortfolioAnalyzer, StockRecommendationEngine
import sys
import io

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Market ChatGPT - Next Gen",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .signal-buy {
        color: #00cc44;
        font-weight: bold;
        font-size: 1.2em;
    }
    .signal-sell {
        color: #ff3333;
        font-weight: bold;
        font-size: 1.2em;
    }
    .signal-hold {
        color: #ffa500;
        font-weight: bold;
        font-size: 1.2em;
    }
    .confidence-high {
        background-color: #d4edda;
        color: #155724;
    }
    .confidence-medium {
        background-color: #fff3cd;
        color: #856404;
    }
    .confidence-low {
        background-color: #f8d7da;
        color: #721c24;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = {}

# Initialize components
stock_connector = StockDataConnector()
news_connector = NewsSentimentConnector()
orchestrator = SimpleMarketIntelligenceOrchestrator()

# ==================== Helper Functions ====================

def format_confidence(confidence: float) -> str:
    """Format confidence score with color coding"""
    pct = f"{confidence:.0%}"
    if confidence >= 0.7:
        css_class = "confidence-high"
    elif confidence >= 0.5:
        css_class = "confidence-medium"
    else:
        css_class = "confidence-low"
    return pct

def display_agent_reasoning(analysis: Dict) -> None:
    """Display agent reasoning in expandable sections"""
    with st.expander("📊 View Agent Reasoning & Data"):
        if 'analysis' in analysis:
            st.text_area(
                "Full Agent Analysis",
                value=analysis['analysis'],
                height=400,
                disabled=True,
                label_visibility="collapsed"
            )
        else:
            st.info("No detailed reasoning available")

def create_quick_analysis(symbol: str) -> Dict:
    """Create a quick stock analysis without full CrewAI workflow"""
    try:
        # Resolve ticker
        ticker = stock_connector.resolve_ticker(symbol)
        if not ticker:
            return {'error': f'Could not resolve ticker for {symbol}'}
        
        # Fetch data
        data = stock_connector.get_stock_data(ticker, period="3mo")
        if data is None or data.empty:
            return {'error': f'No data available for {symbol}'}
        
        # Get live price
        live_price = stock_connector.get_live_price(ticker)
        
        # Technical analysis
        tech_signal = TechnicalAnalyzer.get_technical_signal(data)
        
        # Sentiment analysis
        sentiment = news_connector.get_company_sentiment(symbol, days=7)
        
        # Fundamentals
        fundamentals = stock_connector.get_fundamental_data(ticker)
        
        # Synthesize recommendation
        recommendation = StockRecommendationEngine.synthesize_recommendation(
            tech_signal, sentiment, fundamentals or {}
        )
        
        return {
            'symbol': symbol,
            'ticker': ticker,
            'live_price': live_price,
            'technical_signal': tech_signal,
            'sentiment': sentiment,
            'fundamentals': fundamentals,
            'recommendation': recommendation
        }
    except Exception as e:
        logger.error(f"Error in quick analysis: {str(e)}")
        return {'error': str(e)}

# ==================== Main App ====================

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📈 Market ChatGPT - Next Generation</h1>
        <p>AI-Powered Stock Analysis with Multi-Agent Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for navigation and portfolio
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        app_mode = st.radio(
            "Select Mode",
            ["💬 Market Chat", "📊 Stock Analysis", "🎯 Portfolio Audit", "📚 Demo Scenarios"]
        )
        
        st.divider()
        
        # Portfolio section
        st.subheader("💼 Your Portfolio")
        portfolio_option = st.radio(
            "Portfolio Input",
            ["Use Sample Portfolio", "Upload CSV", "Manual Entry"]
        )
        
        if portfolio_option == "Use Sample Portfolio":
            st.session_state.portfolio = SAMPLE_PORTFOLIO
            st.success("Sample portfolio loaded!")
            with st.expander("View Portfolio"):
                df = pd.DataFrame(st.session_state.portfolio)
                st.dataframe(df[['symbol', 'sector', 'quantity', 'current_price', 'return_pct']], use_container_width=True)
        
        elif portfolio_option == "Upload CSV":
            uploaded_file = st.file_uploader("Upload portfolio CSV", type="csv")
            if uploaded_file:
                df = pd.read_csv(uploaded_file)
                st.session_state.portfolio = df.to_dict('records')
                st.success("Portfolio uploaded!")
        
        elif portfolio_option == "Manual Entry":
            col1, col2 = st.columns(2)
            with col1:
                symbol = st.text_input("Stock Symbol")
            with col2:
                qty = st.number_input("Quantity", min_value=1)
            if st.button("Add to Portfolio"):
                st.session_state.portfolio.append({
                    'symbol': symbol,
                    'quantity': qty
                })
                st.success(f"Added {qty} shares of {symbol}")
        
        st.divider()
        st.info("💡 **Tip**: Market ChatGPT analyzes stocks across technical, sentiment, and fundamental factors for multi-factor recommendations.")
    
    # ==================== Main Content ====================
    
    if app_mode == "💬 Market Chat":
        st.subheader("🤖 Chat with Market Intelligence Agent")
        
        # Chat interface
        chat_container = st.container()
        input_container = st.container()
        
        # Display chat history
        for i, message in enumerate(st.session_state.chat_history):
            if message['role'] == 'user':
                st.chat_message("user").write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
                    if 'reasoning' in message:
                        with st.expander("View Agent Reasoning"):
                            st.text(message['reasoning'])
        
        # Chat input
        with input_container:
            user_query = st.text_input(
                "Ask about stocks, portfolio, sectors, or market trends:",
                placeholder="e.g., 'Should I buy Infosys?', 'Is my portfolio overconcentrated?'"
            )
            
            if user_query:
                # Add user message to history
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_query,
                    'timestamp': datetime.now()
                })
                
                # Process query
                st.info("🔄 Analyzing with multiple agents...")
                
                # Simple NLP-based query routing (MVP approach)
                if any(word in user_query.lower() for word in ['should i buy', 'is', 'good', 'buy', 'sell', 'hold']):
                    # Extract symbol from query
                    words = user_query.split()
                    symbol = next((word for word in words if word.upper() in ['TCS', 'INFOSYS', 'RELIANCE', 'HDFCBANK', 'WIPRO', 'ITC']), None)
                    
                    if symbol:
                        analysis = create_quick_analysis(symbol)
                        
                        if 'error' not in analysis:
                            # Build response
                            response = f"""
### Analysis for {symbol}

**Recommendation**: {analysis['recommendation']['recommendation']}
**Confidence**: {format_confidence(analysis['recommendation']['confidence'])}

**Key Factors**:
"""
                            for factor in analysis['recommendation'].get('key_factors', []):
                                response += f"\n- {factor}"
                            
                            response += f"\n\n**Technicals**: {analysis['technical_signal']['signal']} (RSI: {analysis['technical_signal']['rsi']:.0f})"
                            response += f"\nSentiment: {analysis['sentiment']['sentiment']}"
                            response += f"\n\n⚠️ {analysis['recommendation']['disclaimer']}"
                            
                            st.session_state.chat_history.append({
                                'role': 'assistant',
                                'content': response,
                                'reasoning': analysis.get('analysis', ''),
                                'timestamp': datetime.now()
                            })
                            
                            st.markdown(response)
                            display_agent_reasoning(analysis)
                    else:
                        response = "I couldn't identify a specific stock in your query. Try asking: 'Should I buy TCS?' or 'Is Infosys a good buy?'"
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now()
                        })
                        st.markdown(response)
                
                elif 'portfolio' in user_query.lower():
                    if st.session_state.portfolio:
                        analysis = PortfolioAnalyzer.analyze_concentration(st.session_state.portfolio)
                        
                        response = f"""
### Portfolio Analysis

**Concentration Risk**: {analysis['concentration_risk']}
**Max Sector Weight**: {analysis.get('max_sector_weight', 0):.1f}%

**Recommendation**: {analysis.get('recommendation', 'No recommendation available')}

**Sector Breakdown**:
"""
                        for sector, weight in analysis.get('sector_breakdown', {}).items():
                            response += f"\n- {sector}: {weight:.1f}%"
                        
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now()
                        })
                        
                        st.markdown(response)
                    else:
                        response = "Please load or upload a portfolio first to analyze it."
                        st.session_state.chat_history.append({
                            'role': 'assistant',
                            'content': response,
                            'timestamp': datetime.now()
                        })
                        st.markdown(response)
                
                else:
                    response = "I can help with:\n- Stock buy/sell/hold recommendations\n- Portfolio risk analysis\n- Sector trends\n\nTry asking: 'Should I buy TCS?' or 'Is my portfolio overconcentrated?'"
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response,
                        'timestamp': datetime.now()
                    })
                    st.markdown(response)
                
                st.rerun()
    
    elif app_mode == "📊 Stock Analysis":
        st.subheader("🔍 Detailed Stock Analysis")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            symbol = st.text_input(
                "Enter Stock Symbol",
                placeholder="TCS, Infosys, Reliance, etc.",
                label_visibility="collapsed"
            )
        
        with col2:
            analyze_btn = st.button("Analyze", use_container_width=True, type="primary")
        
        if analyze_btn and symbol:
            with st.spinner("Analyzing stock with AI agents..."):
                analysis = create_quick_analysis(symbol)
                
                if 'error' not in analysis:
                    # Create tabs for different analysis views
                    tab1, tab2, tab3, tab4 = st.tabs(["📊 Summary", "📈 Technical", "💬 Sentiment", "💰 Fundamentals"])
                    
                    with tab1:
                        # Recommendation card
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            rec = analysis['recommendation']['recommendation']
                            if rec == 'BUY':
                                st.markdown(f'<div class="signal-buy">Signal: {rec}</div>', unsafe_allow_html=True)
                            elif rec == 'SELL':
                                st.markdown(f'<div class="signal-sell">Signal: {rec}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(f'<div class="signal-hold">Signal: {rec}</div>', unsafe_allow_html=True)
                        
                        with col2:
                            conf = analysis['recommendation']['confidence']
                            st.metric("Confidence", format_confidence(conf))
                        
                        with col3:
                            if analysis['live_price']:
                                st.metric(
                                    f"{symbol} Price",
                                    f"₹{analysis['live_price']['current_price']:.2f}",
                                    "N/A"
                                )
                        
                        st.divider()
                        
                        st.subheader("Key Factors")
                        for factor in analysis['recommendation'].get('key_factors', []):
                            st.write(f"- {factor}")
                        
                        st.warning(analysis['recommendation'].get('disclaimer', ''))
                    
                    with tab2:
                        st.subheader("Technical Analysis")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.metric("RSI (14)", f"{analysis['technical_signal']['rsi']:.0f}")
                        with col2:
                            st.metric("Signal", analysis['technical_signal']['signal'])
                        
                        st.info(analysis['technical_signal'].get('reasoning', 'No technical reasoning available'))
                        
                        if analysis['technical_signal'].get('divergence', {}).get('divergence_type') != 'NONE':
                            st.success(f"🔄 {analysis['technical_signal']['divergence']['description']}")
                    
                    with tab3:
                        st.subheader("Sentiment Analysis")
                        
                        sentiment = analysis['sentiment']
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric("Sentiment", sentiment['sentiment'], f"Score: {sentiment['score']:.2f}")
                        with col2:
                            st.metric("Articles Analyzed", sentiment['articles_analyzed'])
                        
                        st.write(sentiment['reasoning'])
                        
                        if sentiment.get('top_articles'):
                            st.subheader("Recent News")
                            for article in sentiment['top_articles']:
                                st.write(f"- {article['title']}")
                    
                    with tab4:
                        st.subheader("Fundamental Data")
                        
                        if analysis.get('fundamentals'):
                            fund = analysis['fundamentals']
                            
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("P/E Ratio", fund.get('pe_ratio', 'N/A'))
                            with col2:
                                st.metric("Sector", fund.get('sector', 'N/A'))
                            with col3:
                                st.metric("Market Cap", fund.get('market_cap', 'N/A'))
                            
                            st.write(f"**Company**: {fund.get('company_name', 'N/A')}")
                            st.write(f"**ROE**: {fund.get('roe', 'N/A')}")
                            st.write(f"**Debt/Equity**: {fund.get('debt_to_equity', 'N/A')}")
                        else:
                            st.info("Fundamentals not available for this stock")
                    
                    display_agent_reasoning(analysis)
                else:
                    st.error(f"Error: {analysis.get('error', 'Unknown error')}")
    
    elif app_mode == "🎯 Portfolio Audit":
        st.subheader("📊 Portfolio Risk Analysis")
        
        if st.session_state.portfolio:
            if st.button("Run Portfolio Audit", type="primary", use_container_width=True):
                with st.spinner("Analyzing portfolio..."):
                    analysis = PortfolioAnalyzer.analyze_concentration(st.session_state.portfolio)
                    
                    # Overview metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Portfolio Value", f"₹{analysis.get('total_portfolio_value', 0):,.0f}")
                    with col2:
                        risk = analysis.get('concentration_risk', 'UNKNOWN')
                        st.metric("Concentration Risk", risk)
                    with col3:
                        st.metric("Max Sector", f"{analysis.get('max_sector_weight', 0):.1f}%")
                    
                    st.divider()
                    
                    # Sector breakdown
                    st.subheader("Sector Breakdown")
                    if analysis.get('sector_breakdown'):
                        sector_df = pd.DataFrame(
                            list(analysis['sector_breakdown'].items()),
                            columns=['Sector', 'Weight %']
                        )
                        col1, col2 = st.columns([2, 1])
                        with col1:
                            st.bar_chart(sector_df.set_index('Sector'))
                        with col2:
                            st.dataframe(sector_df, use_container_width=True)
                    
                    # Top positions
                    st.subheader("Top Positions")
                    if analysis.get('top_positions'):
                        top_df = pd.DataFrame(analysis['top_positions'])
                        st.dataframe(top_df, use_container_width=True)
                    
                    # Recommendation
                    st.info(f"**Recommendation**: {analysis.get('recommendation', 'No recommendation')}")
        else:
            st.warning("Please load a portfolio first (check sidebar configuration)")
    
    elif app_mode == "📚 Demo Scenarios":
        st.subheader("🎬 Try Demo Scenarios")
        
        selected_scenario = st.selectbox(
            "Choose a demo scenario",
            list(DEMO_SCENARIOS.keys()),
            format_func=lambda x: DEMO_SCENARIOS[x]['title']
        )
        
        scenario = DEMO_SCENARIOS[selected_scenario]
        
        with st.container():
            st.write(f"**Scenario**: {scenario['title']}")
            st.write(f"**Context**: {scenario.get('context', 'N/A')}")
            st.divider()
            
            if st.button("Run This Scenario", type="primary", use_container_width=True):
                with st.spinner("Running scenario analysis..."):
                    if 'symbol' in scenario:
                        analysis = create_quick_analysis(scenario['symbol'])
                        
                        if 'error' not in analysis:
                            st.success(f"Analysis for {scenario['symbol']}")
                            
                            rec = analysis['recommendation']
                            st.markdown(f"**Recommendation**: **{rec['recommendation']}** ({format_confidence(rec['confidence'])})")
                            
                            st.write("**Key Factors**:")
                            for factor in rec.get('key_factors', []):
                                st.write(f"- {factor}")
                            
                            # Show metrics
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Technical", analysis['technical_signal']['signal'])
                            with col2:
                                st.metric("Sentiment", analysis['sentiment']['sentiment'])
                            with col3:
                                st.metric("RSI", f"{analysis['technical_signal']['rsi']:.0f}")
                            
                            with st.expander("View Full Analysis"):
                                st.text(str(analysis))

if __name__ == "__main__":
    main()
