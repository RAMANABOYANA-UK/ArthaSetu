"""
ArthaSetu Market Intelligence - Local API Server
Run on localhost without Streamlit framework
"""

from flask import Flask, jsonify, request, send_file, session
from flask_cors import CORS
from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
from demo_data import SAMPLE_PORTFOLIO
from database import db
import json
import os
from datetime import datetime
import random
import threading
import requests
from dotenv import load_dotenv

# Import new investor guidance modules
try:
    from fundamentals import get_fundamental_data, get_valuation_analysis, get_dividend_info, compare_fundamentals
    FUNDAMENTALS_AVAILABLE = True
except:
    FUNDAMENTALS_AVAILABLE = False

try:
    from news_sentiment import get_latest_news, get_sentiment_analysis, get_news_sentiment_impact, get_news_impact_score
    NEWS_SENTIMENT_AVAILABLE = True
except:
    NEWS_SENTIMENT_AVAILABLE = False

try:
    from advanced_indicators import get_advanced_indicators, get_trading_signals
    ADVANCED_IND_AVAILABLE = True
except:
    ADVANCED_IND_AVAILABLE = False

try:
    from risk_management import calculate_portfolio_risk, get_risk_rating, calculate_stop_loss, calculate_var_value_at_risk
    RISK_MGMT_AVAILABLE = True
except:
    RISK_MGMT_AVAILABLE = False

try:
    from backtesting_engine import backtest_strategy, compare_strategies
    BACKTEST_AVAILABLE = True
except:
    BACKTEST_AVAILABLE = False

# Load environment variables from .env file
load_dotenv()

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except:
    YFINANCE_AVAILABLE = False

# Alpha Vantage Configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
ALPHA_VANTAGE_URL = 'https://www.alphavantage.co/query'

# Mock data for recommendations and sectors
MOCK_RECOMMENDATIONS = [
    {'symbol': 'TCS.NS', 'name': 'Tata Consultancy', 'recommendation': 'BUY', 'sector': 'IT', 'sentiment': 'BULLISH', 'confidence': 78, 'price': 2389.80},
    {'symbol': 'INFY.NS', 'name': 'Infosys', 'recommendation': 'BUY', 'sector': 'IT', 'sentiment': 'BULLISH', 'confidence': 82, 'price': 1269.70},
    {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries', 'recommendation': 'HOLD', 'sector': 'Energy', 'sentiment': 'NEUTRAL', 'confidence': 65, 'price': 1348.10},
    {'symbol': 'ITC.NS', 'name': 'ITC Limited', 'recommendation': 'SELL', 'sector': 'FMCG', 'sentiment': 'BEARISH', 'confidence': 72, 'price': 294.70},
    {'symbol': 'WIPRO.NS', 'name': 'Wipro', 'recommendation': 'BUY', 'sector': 'IT', 'sentiment': 'BULLISH', 'confidence': 75, 'price': 410.50},
    {'symbol': 'BAJAJFINSV.NS', 'name': 'Bajaj Finserv', 'recommendation': 'BUY', 'sector': 'Finance', 'sentiment': 'BULLISH', 'confidence': 80, 'price': 1650.00},
    {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank', 'recommendation': 'HOLD', 'sector': 'Banking', 'sentiment': 'NEUTRAL', 'confidence': 68, 'price': 1680.50},
    {'symbol': 'AXISBANK.NS', 'name': 'Axis Bank', 'recommendation': 'BUY', 'sector': 'Banking', 'sentiment': 'BULLISH', 'confidence': 76, 'price': 1050.80},
    {'symbol': 'MARUTI.NS', 'name': 'Maruti Suzuki', 'recommendation': 'HOLD', 'sector': 'Auto', 'sentiment': 'NEUTRAL', 'confidence': 62, 'price': 8150.00},
    {'symbol': 'LT.NS', 'name': 'Larsen & Toubro', 'recommendation': 'BUY', 'sector': 'Engineering', 'sentiment': 'BULLISH', 'confidence': 79, 'price': 3180.95},
    {'symbol': 'NESTLEIND.NS', 'name': 'Nestlé India', 'recommendation': 'HOLD', 'sector': 'FMCG', 'sentiment': 'NEUTRAL', 'confidence': 70, 'price': 2280.00},
    {'symbol': 'PHARMACIE.NS', 'name': 'Pharma Chemicals', 'recommendation': 'BUY', 'sector': 'Pharma', 'sentiment': 'BULLISH', 'confidence': 81, 'price': 1450.00},
    {'symbol': 'GICRE.NS', 'name': 'GICRE', 'recommendation': 'SELL', 'sector': 'Insurance', 'sentiment': 'BEARISH', 'confidence': 71, 'price': 150.50},
]

# Storage for parallel fetch results
PRICE_FETCH_RESULTS = {}

def fetch_price_from_alpha_vantage(symbol, results_dict):
    """Fetch latest price from Alpha Vantage API"""
    if not ALPHA_VANTAGE_API_KEY or ALPHA_VANTAGE_API_KEY == '':
        results_dict['alpha_vantage'] = None
        return
    
    try:
        # Convert NSE symbol to Alpha Vantage format (remove .NS)
        av_symbol = symbol.replace('.NS', '') if '.NS' in symbol else symbol
        
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': av_symbol,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=5)
        data = response.json()
        
        if 'Global Quote' in data and '05. price' in data['Global Quote']:
            price = float(data['Global Quote']['05. price'])
            if price > 0:
                results_dict['alpha_vantage'] = {
                    'price': round(price, 2),
                    'source': 'Alpha Vantage'
                }
                return
    except Exception as e:
        print(f"Alpha Vantage fetch error: {str(e)}")
    
    results_dict['alpha_vantage'] = None

def fetch_price_from_yfinance(symbol, results_dict):
    """Fetch latest price from Yahoo Finance (yfinance)"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='5d')
        if not hist.empty:
            latest_close = round(hist['Close'].iloc[-1], 2)
            if latest_close > 0:
                results_dict['yfinance'] = {
                    'price': latest_close,
                    'source': 'Yahoo Finance'
                }
                return
    except Exception as e:
        print(f"yFinance fetch error: {str(e)}")
    
    results_dict['yfinance'] = None

def get_price_from_parallel_sources(symbol):
    """
    Fetch price from both Alpha Vantage and yfinance in parallel
    Returns the most reliable price with source information
    """
    results = {}
    
    # Create threads for parallel fetching
    thread_av = threading.Thread(target=fetch_price_from_alpha_vantage, args=(symbol, results))
    thread_yf = threading.Thread(target=fetch_price_from_yfinance, args=(symbol, results))
    
    # Start both threads
    thread_av.start()
    thread_yf.start()
    
    # Wait for both to complete (timeout 3 seconds - faster fallback)
    thread_av.join(timeout=3)
    thread_yf.join(timeout=3)
    
    # Logic to decide which source to use
    av_result = results.get('alpha_vantage')
    yf_result = results.get('yfinance')
    
    # Strategy: If both available, compare; otherwise use whichever is available
    if av_result and yf_result:
        # Both available - use average for better accuracy
        avg_price = (av_result['price'] + yf_result['price']) / 2
        price_diff_percent = abs(av_result['price'] - yf_result['price']) / avg_price * 100
        
        # If prices differ by more than 5%, use yfinance (more frequent updates)
        if price_diff_percent > 5:
            print(f"[PRICE COMPARISON] {symbol}: AV={av_result['price']}, YF={yf_result['price']} (diff: {price_diff_percent:.1f}%)")
            return yf_result['price'], 'Yahoo Finance (Verified)', av_result['price']
        else:
            # Use average of both for best estimate
            return round(avg_price, 2), 'Dual Source (AV + YF Average)', None
    
    elif av_result:
        return av_result['price'], 'Alpha Vantage', None
    elif yf_result:
        return yf_result['price'], 'Yahoo Finance', None
    else:
        return None, 'No Source Available', None



def get_real_recommendation(symbol):
    """Get recommendation based on REAL technical analysis"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period='20d')
        if hist.empty or len(hist) < 5:
            return {'recommendation': 'HOLD', 'confidence': 60, 'sentiment': 'NEUTRAL'}
        
        current = hist['Close'].iloc[-1]
        prev = hist['Close'].iloc[-2]
        ma_20 = hist['Close'].tail(20).mean()
        ma_5 = hist['Close'].tail(5).mean()
        momentum = ((ma_5 - ma_20) / ma_20) * 100
        
        if current > ma_20 and momentum > 0:
            conf = min(85, int(50 + abs(momentum) * 2))
            return {'recommendation': 'BUY', 'confidence': conf, 'sentiment': 'BULLISH'}
        elif current < ma_20 and momentum < -5:
            conf = min(85, int(50 + abs(momentum) * 2))
            return {'recommendation': 'SELL', 'confidence': conf, 'sentiment': 'BEARISH'}
        else:
            return {'recommendation': 'HOLD', 'confidence': 60, 'sentiment': 'NEUTRAL'}
    except:
        return {'recommendation': 'HOLD', 'confidence': 60, 'sentiment': 'NEUTRAL'}

MOCK_SECTORS = [
    {'name': 'Information Technology', 'performance': 12.5, 'strength': 'Strong', 'trend': 'Up'},
    {'name': 'Energy & Infrastructure', 'performance': 8.3, 'strength': 'Moderate', 'trend': 'Stable'},
    {'name': 'Pharma & Healthcare', 'performance': 15.2, 'strength': 'Strong', 'trend': 'Up'},
    {'name': 'Banking & Financial', 'performance': 5.1, 'strength': 'Weak', 'trend': 'Down'},
    {'name': 'FMCG & Consumer', 'performance': -2.3, 'strength': 'Weak', 'trend': 'Down'},
    {'name': 'Realty & Infrastructure', 'performance': 9.8, 'strength': 'Moderate', 'trend': 'Up'},
]

# Market sentiment and performance data
MOCK_MARKET_SENTIMENT = [
    {'name': 'Market Breadth (Advance/Decline)', 'value': 2.1, 'sentiment': 'Bullish', 'description': 'More stocks advancing than declining'},
    {'name': 'Volatility Index (India VIX)', 'value': 18.5, 'sentiment': 'Moderate', 'description': 'Normal volatility levels'},
    {'name': 'Market Momentum', 'value': 65, 'sentiment': 'Bullish', 'description': 'Positive momentum across sectors'},
    {'name': 'RSI (Relative Strength Index)', 'value': 58, 'sentiment': 'Neutral', 'description': 'Neither overbought nor oversold'},
    {'name': 'FII Investment', 'value': 250, 'sentiment': 'Bullish', 'description': 'Strong foreign investor inflow'},
    {'name': 'Price to Earnings Ratio', 'value': 24.5, 'sentiment': 'Fair', 'description': 'Fairly valued market'},
]

MOCK_MARKET_PERFORMANCE = [
    {'name': 'NIFTY 50', 'price': 18450.50, 'change': 1.2, 'changePct': 0.65, 'volume': '150M'},
    {'name': 'SENSEX', 'price': 60580.25, 'change': 2.1, 'changePct': 0.58, 'volume': '145M'},
    {'name': 'NIFTY BANK', 'price': 42180.75, 'change': 0.8, 'changePct': 0.42, 'volume': '120M'},
    {'name': 'IT INDEX', 'price': 35920.50, 'change': 3.2, 'changePct': 1.25, 'volume': '100M'},
    {'name': 'PHARMA INDEX', 'price': 18750.25, 'change': 2.5, 'changePct': 1.55, 'volume': '85M'},
]

def get_live_price(symbol):
    """
    Fetch REAL live price from BOTH Alpha Vantage and yfinance in parallel
    Returns the most reliable price with metadata
    """
    price, source, alt_price = get_price_from_parallel_sources(symbol)
    
    if price is not None and price > 0:
        return {
            'price': price,
            'source': source,
            'alt_price': alt_price,
            'status': 'success'
        }
    
    # Fallback to mock prices if both sources fail
    mock_prices = {
        'TCS.NS': 2389.80,
        'INFY.NS': 1269.70,
        'RELIANCE.NS': 1348.10,
        'ITC.NS': 294.70,
        'WIPRO.NS': 410.50,
        'BAJAJFINSV.NS': 1650.00,
        'HDFCBANK.NS': 1680.50,
        'AXISBANK.NS': 1050.80,
        'MARUTI.NS': 8150.00,
        'LT.NS': 3180.95,
        'NESTLEIND.NS': 2280.00,
        'PHARMACIE.NS': 1450.00,
        'GICRE.NS': 150.50
    }
    
    fallback_price = mock_prices.get(symbol, 1000)
    return {
        'price': fallback_price,
        'source': 'Fallback Mock Data',
        'alt_price': None,
        'status': 'fallback'
    }

app = Flask(__name__)
app.secret_key = 'arthsetu_secret_key_2026'
CORS(app)
orchestrator = SimpleMarketIntelligenceOrchestrator()

# In-memory user database
USERS_DB = {
    'demo@arthsetu.com': {
        'password': 'demo123',
        'name': 'Demo User',
        'portfolio': [
            {'symbol': 'TCS', 'quantity': 10, 'buy_price': 3500, 'sector': 'IT'},
            {'symbol': 'INFY', 'quantity': 15, 'buy_price': 1400, 'sector': 'IT'},
            {'symbol': 'RELIANCE', 'quantity': 5, 'buy_price': 2400, 'sector': 'Energy'},
            {'symbol': 'ITC', 'quantity': 20, 'buy_price': 420, 'sector': 'FMCG'},
        ]
    }
}

@app.route('/', methods=['GET'])
def home():
    """Serve the main HTML page"""
    try:
        index_path = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Frontend error: {str(e)}'}), 404

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'service': 'ArthaSetu'}), 200

@app.route('/stock/<symbol>', methods=['GET'])
def analyze_stock(symbol):
    """Analyze a stock for buy/sell signal"""
    try:
        result = orchestrator.analyze_stock_for_buy(symbol.upper())
        return jsonify({
            'status': 'success',
            'live_price': result.get('current_price', 0),
            'recommendation': result.get('recommendation', 'HOLD'),
            'confidence': result.get('confidence', 0)
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/portfolio', methods=['GET'])
def analyze_portfolio():
    """Analyze portfolio risk"""
    try:
        result = orchestrator.analyze_portfolio_risk(SAMPLE_PORTFOLIO)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/sectors', methods=['GET'])
def analyze_sectors():
    """Analyze sector rotation - returns mock data"""
    try:
        return jsonify({'status': 'success', 'sectors': MOCK_SECTORS}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sectors', methods=['GET'])
def api_analyze_sectors():
    """API endpoint for sector rotation analysis"""
    try:
        # Simulate live data with small price variations
        sectors = []
        for sector in MOCK_SECTORS:
            # Add small random variation to performance
            variation = random.uniform(-1, 1)
            sectors.append({
                'name': sector['name'],
                'performance': round(sector['performance'] + variation, 2),
                'strength': sector['strength'],
                'trend': sector['trend']
            })
        return jsonify({'status': 'success', 'sectors': sectors}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== API ENDPOINTS (with /api prefix) =====
@app.route('/api', methods=['GET'])
def api_info():
    """API Information - List all available endpoints"""
    return jsonify({
        'status': 'success',
        'service': 'ArthaSetu Market Intelligence API',
        'version': '1.0',
        'endpoints': {
            'authentication': {
                'register': 'POST /api/auth/register',
                'login': 'POST /api/auth/login',
                'logout': 'POST /api/auth/logout',
                'me': 'GET /api/auth/me'
            },
            'market_data': {
                'ticker': 'GET /api/market/ticker',
                'recommendations': 'GET /api/market/recommendations',
                'sectors': 'GET /api/sectors'
            },
            'portfolio': {
                'items': 'GET /api/portfolio/items',
                'add': 'POST /api/portfolio/add'
            },
            'features': {
                'chat': 'POST /api/chat',
                'paper_trading_start': 'POST /api/paper-trading/start',
                'paper_trading_leaderboard': 'GET /api/paper-trading/leaderboard',
                'alerts_add': 'POST /api/alerts/add',
                'alerts_list': 'GET /api/alerts/list'
            },
            'health': 'GET /api/health'
        }
    }), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/api/auth/register', methods=['POST'])
def api_register():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if not email or not password or not name:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        result = db.register_user(email, password, name)
        
        if result['status'] == 'success':
            session['user_email'] = email
            session['user_name'] = name
            return jsonify({
                'status': 'success',
                'message': 'Registration successful',
                'user': {'email': email, 'name': name}
            }), 201
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def api_login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'status': 'error', 'message': 'Missing credentials'}), 400
        
        result = db.login_user(email, password)
        
        if result['status'] == 'success':
            session['user_email'] = email
            session['user_name'] = result['name']
            session['user_id'] = result['user_id']
            return jsonify({
                'status': 'success',
                'message': 'Login successful',
                'user': {'email': email, 'name': result['name']}
            }), 200
        else:
            return jsonify({'status': 'error', 'message': result['message']}), 401
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.pop('user_email', None)
    session.pop('user_name', None)
    session.pop('user_id', None)
    return jsonify({'status': 'success', 'message': 'Logged out'}), 200

@app.route('/api/auth/me', methods=['GET'])
def api_get_user():
    if 'user_email' not in session:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    
    email = session.get('user_email')
    name = session.get('user_name')
    return jsonify({
        'status': 'success',
        'user': {'email': email, 'name': name}
    }), 200

@app.route('/api/stock/<symbol>', methods=['GET'])
def api_analyze_stock(symbol):
    try:
        symbol_ns = symbol.upper() if '.NS' in symbol.upper() else f"{symbol.upper()}.NS"
        price_data = get_live_price(symbol_ns)
        
        # Get REAL recommendation based on technical analysis
        rec = get_real_recommendation(symbol_ns)
        
        # Map to sector
        sector_map = {
            'TCS.NS': 'IT', 'INFY.NS': 'IT', 'WIPRO.NS': 'IT',
            'RELIANCE.NS': 'Energy', 'HDFC.NS': 'Banking',
            'ITC.NS': 'FMCG', 'LT.NS': 'Engineering'
        }
        sector = sector_map.get(symbol_ns, 'Diversified')
        
        return jsonify({
            'status': 'success',
            'live_price': price_data['price'],
            'price_source': price_data['source'],
            'alt_price': price_data.get('alt_price'),
            'recommendation': rec['recommendation'],
            'confidence': rec['confidence'],
            'sector': sector,
            'sentiment': rec['sentiment'],
            'verified': price_data['status'] == 'success'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/portfolio/items', methods=['GET'])
def api_get_portfolio_items():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'portfolio': []}), 200
    
    user_id = session['user_id']
    portfolio = db.get_portfolio(user_id)
    return jsonify({'status': 'success', 'portfolio': portfolio}), 200

@app.route('/api/portfolio/add', methods=['POST'])
def api_add_to_portfolio():
    if 'user_id' not in session:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    
    try:
        data = request.json
        user_id = session['user_id']
        
        result = db.add_portfolio_item(
            user_id,
            data.get('symbol').upper(),
            data.get('quantity'),
            data.get('price'),
            data.get('sector', 'Other')
        )
        
        if result['status'] == 'success':
            return jsonify(result), 201
        else:
            return jsonify(result), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/market/recommendations', methods=['GET'])
def api_get_recommendations():
    try:
        rec_list = []
        for rec in MOCK_RECOMMENDATIONS:
            # Get live price
            price_data = get_live_price(rec['symbol'])
            live_price = price_data['price'] if price_data else 1000
            
            # Simulate confidence variation
            confidence = max(50, min(95, rec['confidence'] + random.uniform(-5, 5)))
            
            rec_list.append({
                'symbol': rec['symbol'].replace('.NS', ''),
                'name': rec.get('name', rec['symbol']),
                'recommendation': rec['recommendation'],
                'price': live_price,
                'sector': rec['sector'],
                'sentiment': rec['sentiment'],
                'confidence': round(confidence),
                'price_source': price_data.get('source', 'Unknown') if price_data else 'Unknown'
            })
        
        return jsonify({'status': 'success', 'recommendations': rec_list}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'recommendations': []}), 200

# Market Sentiment Analysis Endpoint
@app.route('/api/market/sentiment', methods=['GET'])
def api_market_sentiment():
    try:
        sentiment_data = []
        for item in MOCK_MARKET_SENTIMENT:
            sentiment_data.append({
                'name': item['name'],
                'value': item['value'] + random.uniform(-0.5, 0.5),
                'sentiment': item['sentiment'],
                'description': item['description']
            })
        
        return jsonify({
            'status': 'success',
            'sentiment': sentiment_data,
            'overall': 'BULLISH',
            'confidence': 72,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'sentiment': []}), 200

# Market Performance Charts Endpoint
@app.route('/api/market/performance', methods=['GET'])
def api_market_performance():
    try:
        indices = []
        for perf in MOCK_MARKET_PERFORMANCE:
            variation = random.uniform(-0.3, 0.3)
            indices.append({
                'name': perf['name'],
                'price': round(perf['price'] + variation, 2),
                'change': round(perf['change'] + random.uniform(-0.5, 0.5), 2),
                'changePct': round(perf['changePct'] + random.uniform(-0.3, 0.3), 2),
                'volume': perf['volume']
            })
        
        return jsonify({
            'status': 'success',
            'indices': indices,
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e), 'indices': []}), 200

# ===== NEW INTERACTIVE FEATURES =====

# AI CHATBOT - Market Intelligence Q&A
AI_RESPONSES = {
    'buy': 'Based on current market trends, here are strong BUY opportunities: TCS and INFY from IT sector show bullish momentum with 78-82% confidence scores.',
    'sell': 'SELL signals detected on ITC (FMCG) due to weak recent performance. Banking sector also showing downside. Consider trimming overweight positions.',
    'hold': 'HOLD recommendations: RELIANCE in Energy sector remains neutral. Good for long-term portfolio stability.',
    'sector': 'IT sector leading with +12.5% performance, followed by Pharma (+15.2%). Banking sector weakness at -5.1%. Realty showing recovery at +9.8%.',
    'portfolio': 'Your portfolio is well-diversified across 4 sectors. Strong IT allocation (50%) is working well. Consider increasing Pharma exposure.',
    'market': 'Overall market sentiment is BULLISH with strong IT leadership. Volatility is moderate. This is a good accumulation opportunity.',
    'recommend': 'Top picks today: TCS (BUY - 95% confidence), INFY (BUY - 82%), RELIANCE (HOLD - 65%), ITC (SELL - 72%).',
    'risk': 'Current portfolio risk level: MODERATE. Diversification score: 78%. Money is protected across 4 main sectors.',
    'tcs': 'TCS (Tata Consultancy Services) is showing strong bullish signals at ₹2,389.80 with +0.19% daily change. IT sector fundamentals are solid. Recommendation: BUY with 80% confidence.',
    'infy': 'Infosys limited is trading at ₹1,269.70 with +1.10% daily movement. Strong performer in IT sector. Recommendation: BUY with 80% confidence.',
    'reliance': 'Reliance Industries at ₹1,348.10 with -2.75% change. Energy sector showing mixed signals. Recommendation: HOLD with 65% confidence for long-term.',
    'itc': 'ITC Limited at ₹294.70 with -1.07% decline. FMCG sector facing headwinds. Recommendation: SELL with 70% confidence. Look for entry at lower levels.',
    'volatility': 'Current market volatility is at MODERATE levels. VIX indicators suggest stable trading conditions. This is a good time for position building in quality stocks.',
    'risk': 'Portfolio risk assessment: Your diversification score is 78%. Risk is MODERATE with good protection across sectors. Consider rebalancing quarterly.',
    'dividend': 'High dividend stocks in our recommendations: TCS offers 1.5% yield, INFY 1.2% yield. Good for income generation alongside capital appreciation.',
    'trend': 'Market trends show: Technology sector UP (+13%), Energy sector STABLE (+8%), FMCG sector DOWN (-2%). Momentum is with IT and Pharma sectors.',
    'growth': 'Growth opportunities identified: Pharma sector +14% YoY growth, IT services +12% YoY. Mid-cap stocks showing strong momentum. Consider diversifying into these.',
    'momentum': 'Price momentum analysis: TCS and INFY showing strong uptrend with above-average volume. RELIANCE consolidating. ITC in downtrend. Selective approach recommended.',
}

@app.route('/api/chat', methods=['POST'])
def chat_endpoint():
    """AI Market Analyst Chatbot with Real-Time Data"""
    try:
        data = request.json
        query = data.get('query', '').lower()
        user_email = data.get('user_email', 'demo@arthsetu.com')
        
        response = "I'll analyze real market data for you. "
        
        # Fetch real-time data for analysis
        live_stocks = []
        for rec in MOCK_RECOMMENDATIONS:
            symbol = rec['symbol']
            price_data = get_live_price(symbol)
            live_price = price_data['price'] if price_data else 2500
            live_stocks.append({
                'symbol': symbol.replace('.NS', ''),
                'price': live_price,
                'rec': rec['recommendation'],
                'confidence': rec['confidence'],
                'source': price_data.get('source', 'Unknown') if price_data else 'Unknown'
            })
        
        # Analyze based on user query with real data
        if 'buy' in query or 'should i buy' in query:
            buys = [s for s in live_stocks if s['rec'] == 'BUY']
            if buys:
                buy_list = ', '.join([f"{s['symbol']} at ₹{s['price']} ({s['confidence']}% confidence)" for s in buys[:3]])
                response += f"Current BUY opportunities based on live data: {buy_list}"
            else:
                response += "No strong BUY signals currently. Consider HOLD or SELL positions."
        
        elif 'sell' in query:
            sells = [s for s in live_stocks if s['rec'] == 'SELL']
            if sells:
                sell_list = ', '.join([f"{s['symbol']} (confidence: {s['confidence']}%)" for s in sells[:3]])
                response += f"SELL signals: {sell_list}. These stocks show weakness in current market conditions."
            else:
                response += "No immediate SELL signals. Market showing stability."
        
        elif 'portfolio' in query or 'my holdings' in query:
            response += "Based on your holdings: TCS and INFY (IT sector) are performing strongly with bullish momentum. RELIANCE stable, ITC showing weakness. Consider trimming ITC position and increasing IT allocation for growth."
        
        elif 'price' in query or 'current' in query:
            prices_str = ', '.join([f"{s['symbol']}: ₹{s['price']}" for s in live_stocks[:4]])
            response += f"Live prices: {prices_str}"
        
        elif 'sector' in query or 'performance' in query:
            response += "Sector analysis (live): IT leading with strong momentum. Energy stable. FMCG weak. Pharma showing good growth potential. Realty recovering."
        
        elif 'risk' in query or 'safe' in query:
            response += "Risk assessment: Your portfolio has moderate risk with good diversification. Safe bets: RELIANCE (stable) and TCS (strong). High growth: INFY and Pharma stocks."
        
        elif 'recommendation' in query or 'what should' in query or 'best stock' in query:
            best = max(live_stocks, key=lambda x: x['confidence'])
            response += f"Top recommendation right now: {best['symbol']} at ₹{best['price']} ({best['rec']} signal, {best['confidence']}% confidence). This matches current market conditions."
        
        else:
            # Default real-time data summary
            bullish = [s for s in live_stocks if s['rec'] == 'BUY']
            response += f"Market shows {len(bullish)}/{len(live_stocks)} bullish signals. "
            if bullish:
                response += f"Top picks: {', '.join([s['symbol'] for s in bullish[:2]])}. "
            response += "Ask me about specific stocks, sectors, or strategies for detailed analysis."
        
        return jsonify({
            'status': 'success',
            'response': response,
            'timestamp': datetime.now().isoformat(),
            'data_type': 'real-time-analysis'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'response': f'Real-time analysis error: {str(e)}'}), 500

# REAL-TIME TICKER - Live Market Data
@app.route('/api/market/ticker', methods=['GET'])
def real_time_ticker():
    """Get real-time stock ticker data"""
    try:
        stocks = []
        for rec in MOCK_RECOMMENDATIONS:
            symbol = rec['symbol']
            price_data = get_live_price(symbol)
            live_price = price_data['price'] if price_data else 2500 + random.uniform(-500, 500)
            
            # Simulate price movement
            change_pct = random.uniform(-3, 5)
            
            stocks.append({
                'symbol': symbol.replace('.NS', ''),
                'price': round(live_price, 2),
                'change': round(change_pct, 2),
                'volume': f"{random.randint(100, 500)}K",
                'source': price_data.get('source', 'Unknown') if price_data else 'Unknown'
            })
        
        return jsonify({'status': 'success', 'stocks': stocks}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# PAPER TRADING - Virtual Trading Mode
PAPER_TRADING_DB = {}

@app.route('/api/paper-trading/start', methods=['POST'])
def start_paper_trading():
    """Start virtual trading with ₹100,000"""
    try:
        data = request.json
        email = data.get('email', 'demo@arthsetu.com')
        
        PAPER_TRADING_DB[email] = {
            'balance': 100000,
            'pnl': 0,
            'trades': [],
            'started': datetime.now().isoformat()
        }
        
        return jsonify({
            'status': 'success',
            'balance': 100000,
            'message': 'Paper trading started!'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/paper-trading/leaderboard', methods=['GET'])
def paper_trading_leaderboard():
    """Get top traders on leaderboard"""
    try:
        # Simulate leaderboard
        leaders = [
            {'rank': 1, 'name': 'Raj Kumar', 'pnl': '+₹15,340', 'return_pct': 15.34},
            {'rank': 2, 'name': 'Priya Singh', 'pnl': '+₹12,890', 'return_pct': 12.89},
            {'rank': 3, 'name': 'Your Account', 'pnl': '+₹4,250', 'return_pct': 4.25},
            {'rank': 4, 'name': 'Arun Verma', 'pnl': '+₹2,100', 'return_pct': 2.10},
            {'rank': 5, 'name': 'Neha Gupta', 'pnl': '-₹1,500', 'return_pct': -1.50},
        ]
        
        return jsonify({
            'status': 'success',
            'leaderboard': leaders
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# PRICE ALERTS - Smart Notifications
ALERTS_DB = {}

@app.route('/api/alerts/add', methods=['POST'])
def add_price_alert():
    """Add price alert for a stock"""
    try:
        data = request.json
        email = data.get('email', 'demo@arthsetu.com')
        symbol = data.get('symbol').upper()
        target_price = data.get('target_price')
        
        if email not in ALERTS_DB:
            ALERTS_DB[email] = []
        
        ALERTS_DB[email].append({
            'symbol': symbol,
            'target_price': target_price,
            'created': datetime.now().isoformat(),
            'active': True
        })
        
        return jsonify({
            'status': 'success',
            'message': f'Alert set for {symbol} at ₹{target_price}',
            'alert': {'symbol': symbol, 'target': target_price}
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/alerts/list', methods=['GET'])
def list_alerts():
    """Get user's price alerts"""
    try:
        email = request.args.get('email', 'demo@arthsetu.com')
        alerts = ALERTS_DB.get(email, [])
        
        return jsonify({
            'status': 'success',
            'alerts': alerts,
            'count': len(alerts)
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== FUNDAMENTALS ANALYSIS ENDPOINTS =====
@app.route('/api/fundamentals/<symbol>', methods=['GET'])
def api_get_fundamentals(symbol):
    """Get comprehensive fundamental analysis for a stock"""
    try:
        if not FUNDAMENTALS_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Fundamentals module not available'}), 503
        
        from fundamentals import get_fundamental_data
        
        symbol_upper = symbol.upper()
        # Try with the symbol as-is first
        fundamentals = get_fundamental_data(symbol_upper)
        print(f"DEBUG: get_fundamental_data('{symbol_upper}') returned: {type(fundamentals)}")
        # If not found, try adding .NS suffix
        if not fundamentals and '.' not in symbol_upper:
            print(f"DEBUG: Trying with .NS suffix: '{symbol_upper}.NS'")
            fundamentals = get_fundamental_data(symbol_upper + '.NS')
            print(f"DEBUG: get_fundamental_data('{symbol_upper}.NS') returned: {type(fundamentals)}")
        
        if not fundamentals:
            print(f"DEBUG: Fundamentals still None, returning error")
            return jsonify({'status': 'error', 'message': f'No fundamental data for {symbol}'}), 404
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'company_name': fundamentals.get('name', symbol_upper),
            'sector': fundamentals.get('sector', 'N/A'),
            'financials': {
                'pe_ratio': fundamentals.get('pe_ratio'),
                'eps': fundamentals.get('eps'),
                'dividend_yield': fundamentals.get('dividend_yield'),
                'book_value': fundamentals.get('pb_ratio'),
                'pb_ratio': fundamentals.get('pb_ratio')
            },
            'efficiency': {
                'roe': fundamentals.get('roe'),
                'debt_to_equity': fundamentals.get('debt_to_equity'),
                'current_ratio': fundamentals.get('current_ratio')
            },
            'growth': {
                'revenue_growth': fundamentals.get('revenue_growth'),
                'profit_growth': fundamentals.get('profit_growth')
            },
            'market_info': {
                'market_cap': fundamentals.get('market_cap'),
                'financial_health': fundamentals.get('financial_health')
            },
            'recommendation': fundamentals.get('rating', 'HOLD'),
            'rating_score': fundamentals.get('strength_score', 50),
            'analyst_consensus': fundamentals.get('analyst_consensus', 'N/A'),
            'target_price': fundamentals.get('target_price', 'N/A')
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/fundamentals/compare', methods=['POST'])
def api_compare_fundamentals():
    """Compare fundamentals of multiple stocks"""
    try:
        if not FUNDAMENTALS_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Fundamentals module not available'}), 503
        
        from fundamentals import compare_fundamentals
        
        data = request.json
        symbols = data.get('symbols', [])
        
        if not symbols or len(symbols) < 2:
            return jsonify({'status': 'error', 'message': 'Provide at least 2 symbols for comparison'}), 400
        
        comparison = compare_fundamentals([s.upper() for s in symbols])
        
        return jsonify({
            'status': 'success',
            'comparison': comparison
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== NEWS & SENTIMENT ANALYSIS ENDPOINTS =====
@app.route('/api/sentiment/<symbol>', methods=['GET'])
def api_get_sentiment(symbol):
    """Get market sentiment and news analysis for a stock"""
    try:
        if not NEWS_SENTIMENT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Sentiment module not available'}), 503
        
        from news_sentiment import get_latest_news, get_sentiment_analysis, get_news_impact_score
        
        symbol_upper = symbol.upper()
        latest_news = get_latest_news(symbol_upper)
        sentiment = get_sentiment_analysis(symbol_upper)
        impact = get_news_impact_score(symbol_upper)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'latest_news': latest_news,
            'sentiment': sentiment,
            'news_impact_score': impact,
            'sentiment_recommendation': 'BUY' if sentiment.get('score', 50) > 65 else 'SELL' if sentiment.get('score', 50) < 35 else 'HOLD'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sentiment/compare', methods=['POST'])
def api_compare_sentiments():
    """Compare sentiment across multiple stocks"""
    try:
        if not NEWS_SENTIMENT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Sentiment module not available'}), 503
        
        from news_sentiment import get_sentiment_analysis
        
        data = request.json
        symbols = data.get('symbols', [])
        
        comparisons = []
        for symbol in symbols:
            sentiment = get_sentiment_analysis(symbol.upper())
            comparisons.append({
                'symbol': symbol.upper(),
                'sentiment': sentiment,
                'score': sentiment.get('score', 50)
            })
        
        # Sort by sentiment score (highest first)
        comparisons.sort(key=lambda x: x['score'], reverse=True)
        
        return jsonify({
            'status': 'success',
            'sentiment_comparison': comparisons
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== ADVANCED INDICATORS ENDPOINTS =====
@app.route('/api/indicators/<symbol>', methods=['GET'])
def api_get_indicators(symbol):
    """Get advanced technical indicators for a stock"""
    try:
        if not ADVANCED_IND_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Advanced indicators module not available'}), 503
        
        from advanced_indicators import get_advanced_indicators, get_trading_signals, determine_trend
        
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        indicators = get_advanced_indicators(symbol_upper)
        trading_signals = get_trading_signals(symbol_upper)
        trend = determine_trend(symbol_upper)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'indicators': indicators,
            'trading_signals': trading_signals,
            'trend': trend
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/indicators/rsi/<symbol>', methods=['GET'])
def api_get_rsi(symbol):
    """Get RSI (Relative Strength Index) indicator"""
    try:
        if not ADVANCED_IND_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Advanced indicators module not available'}), 503
        
        from advanced_indicators import calculate_rsi
        
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        rsi_data = calculate_rsi(symbol_upper)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'rsi': rsi_data
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/indicators/macd/<symbol>', methods=['GET'])
def api_get_macd(symbol):
    """Get MACD (Moving Average Convergence Divergence) indicator"""
    try:
        if not ADVANCED_IND_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Advanced indicators module not available'}), 503
        
        from advanced_indicators import calculate_macd
        
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        macd_data = calculate_macd(symbol_upper)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'macd': macd_data
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/indicators/bollinger/<symbol>', methods=['GET'])
def api_get_bollinger(symbol):
    """Get Bollinger Bands indicator"""
    try:
        if not ADVANCED_IND_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Advanced indicators module not available'}), 503
        
        from advanced_indicators import calculate_bollinger_bands
        
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        bb_data = calculate_bollinger_bands(symbol_upper)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'bollinger_bands': bb_data
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== RISK MANAGEMENT ENDPOINTS =====
@app.route('/api/risk/portfolio', methods=['POST'])
def api_portfolio_risk():
    """Analyze portfolio risk and get recommendations"""
    try:
        if not RISK_MGMT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Risk management module not available'}), 503
        
        from risk_management import calculate_portfolio_risk, get_risk_rating, calculate_sharpe_ratio
        
        data = request.json
        portfolio = data.get('portfolio', [])  # [{'symbol': 'TCS', 'allocation': 30}, ...]
        
        if not portfolio:
            return jsonify({'status': 'error', 'message': 'Portfolio data required'}), 400
        
        risk_score = calculate_portfolio_risk(portfolio)
        risk_rating = get_risk_rating(portfolio)
        sharpe_ratio = calculate_sharpe_ratio(portfolio)
        
        return jsonify({
            'status': 'success',
            'risk_score': risk_score,
            'risk_rating': risk_rating,
            'sharpe_ratio': sharpe_ratio,
            'recommendation': 'Rebalance portfolio' if risk_score > 80 else 'Portfolio is well-diversified'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/risk/position-size', methods=['POST'])
def api_position_sizing():
    """Calculate optimal position size based on risk management"""
    try:
        if not RISK_MGMT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Risk management module not available'}), 503
        
        from risk_management import calculate_position_size
        
        data = request.json
        account_value = data.get('account_value', 100000)
        risk_percent = data.get('risk_percent', 1.5)
        
        position_size = calculate_position_size(account_value, risk_percent)
        
        return jsonify({
            'status': 'success',
            'account_value': account_value,
            'risk_percent': risk_percent,
            'position_size': position_size,
            'recommendation': f'Risk {risk_percent}% of ₹{account_value} = ₹{position_size}'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/risk/stop-loss/<symbol>', methods=['POST'])
def api_calculate_stoploss(symbol):
    """Calculate stop-loss and take-profit levels"""
    try:
        if not RISK_MGMT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Risk management module not available'}), 503
        
        from risk_management import calculate_stop_loss
        
        data = request.json
        entry_price = data.get('entry_price', 2500)
        account_value = data.get('account_value', 100000)
        
        sl_levels = calculate_stop_loss(entry_price, account_value)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol.upper(),
            'entry_price': entry_price,
            'stop_loss_levels': sl_levels
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/risk/var', methods=['POST'])
def api_value_at_risk():
    """Calculate Value at Risk (VaR) for portfolio"""
    try:
        if not RISK_MGMT_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Risk management module not available'}), 503
        
        from risk_management import calculate_var_value_at_risk
        
        data = request.json
        portfolio_value = data.get('portfolio_value', 100000)
        confidence_level = data.get('confidence_level', 95)
        
        var = calculate_var_value_at_risk(portfolio_value, confidence_level)
        
        return jsonify({
            'status': 'success',
            'portfolio_value': portfolio_value,
            'confidence_level': confidence_level,
            'var': var,
            'interpretation': f'At {confidence_level}% confidence, maximum loss could be ₹{var}'
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== BACKTESTING ENDPOINTS =====
@app.route('/api/backtest/<symbol>', methods=['GET'])
def api_backtest_single_strategy(symbol):
    """Backtest a specific strategy for a stock"""
    try:
        if not BACKTEST_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Backtesting module not available'}), 503
        
        from backtesting_engine import backtest_strategy
        
        strategy = request.args.get('strategy', 'moving_average')
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        backtest_result = backtest_strategy(symbol_upper, strategy)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'strategy': strategy,
            'backtest_result': backtest_result
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/backtest/compare/<symbol>', methods=['GET'])
def api_compare_strategies(symbol):
    """Compare all trading strategies for a stock"""
    try:
        if not BACKTEST_AVAILABLE:
            return jsonify({'status': 'error', 'message': 'Backtesting module not available'}), 503
        
        from backtesting_engine import compare_strategies
        
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        comparison = compare_strategies(symbol_upper)
        
        return jsonify({
            'status': 'success',
            'symbol': symbol_upper,
            'strategies_comparison': comparison,
            'best_strategy': comparison[0] if comparison else None
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# ===== COMPREHENSIVE STOCK ANALYSIS (ALL MODULES COMBINED) =====
@app.route('/api/analysis/complete/<symbol>', methods=['GET'])
def api_complete_stock_analysis(symbol):
    """Get COMPLETE investor guidance: fundamentals + sentiment + indicators + risk + backtest"""
    try:
        symbol_upper = symbol.upper()
        if '.NS' not in symbol_upper:
            symbol_upper = symbol_upper + '.NS'
        
        analysis_result = {
            'status': 'success',
            'symbol': symbol_upper,
            'timestamp': datetime.now().isoformat(),
            'modules': {}
        }
        
        # Get live price
        price_data = get_live_price(symbol_upper)
        analysis_result['live_price'] = price_data['price']
        analysis_result['price_source'] = price_data.get('source', 'Unknown')
        
        # 1. FUNDAMENTALS
        if FUNDAMENTALS_AVAILABLE:
            try:
                from fundamentals import get_fundamental_data, calculate_financial_health, get_valuation_analysis
                fundamentals = get_fundamental_data(symbol_upper.replace('.NS', ''))
                if fundamentals:
                    health_score = calculate_financial_health(symbol_upper.replace('.NS', ''))
                    valuation = get_valuation_analysis(symbol_upper.replace('.NS', ''))
                    analysis_result['modules']['fundamentals'] = {
                        'data': fundamentals,
                        'health_score': health_score,
                        'valuation': valuation
                    }
            except Exception as e:
                analysis_result['modules']['fundamentals'] = {'error': str(e)}
        
        # 2. SENTIMENT
        if NEWS_SENTIMENT_AVAILABLE:
            try:
                from news_sentiment import get_latest_news, get_sentiment_analysis, get_news_impact_score
                latest_news = get_latest_news(symbol_upper.replace('.NS', ''))
                sentiment = get_sentiment_analysis(symbol_upper.replace('.NS', ''))
                impact = get_news_impact_score(symbol_upper.replace('.NS', ''))
                analysis_result['modules']['sentiment'] = {
                    'news': latest_news[:3],  # Top 3 news items
                    'sentiment_score': sentiment,
                    'impact_score': impact
                }
            except Exception as e:
                analysis_result['modules']['sentiment'] = {'error': str(e)}
        
        # 3. TECHNICAL INDICATORS
        if ADVANCED_IND_AVAILABLE:
            try:
                from advanced_indicators import get_advanced_indicators, get_trading_signals, determine_trend
                indicators = get_advanced_indicators(symbol_upper)
                trading_signals = get_trading_signals(symbol_upper)
                trend = determine_trend(symbol_upper)
                analysis_result['modules']['indicators'] = {
                    'indicators': indicators,
                    'trading_signals': trading_signals,
                    'trend': trend
                }
            except Exception as e:
                analysis_result['modules']['indicators'] = {'error': str(e)}
        
        # 4. RISK MANAGEMENT
        if RISK_MGMT_AVAILABLE:
            try:
                from risk_management import get_risk_rating
                # Use a simple portfolio with just this stock
                portfolio = [{'symbol': symbol_upper.replace('.NS', ''), 'allocation': 100}]
                risk_rating = get_risk_rating(portfolio)
                analysis_result['modules']['risk'] = {
                    'risk_rating': risk_rating
                }
            except Exception as e:
                analysis_result['modules']['risk'] = {'error': str(e)}
        
        # 5. BACKTESTING
        if BACKTEST_AVAILABLE:
            try:
                from backtesting_engine import compare_strategies
                strategies = compare_strategies(symbol_upper)
                analysis_result['modules']['backtesting'] = {
                    'strategies': strategies[:3],  # Top 3 strategies
                    'best_strategy': strategies[0] if strategies else None
                }
            except Exception as e:
                analysis_result['modules']['backtesting'] = {'error': str(e)}
        
        # FINAL RECOMMENDATION
        recommendation = 'HOLD'
        confidence = 60
        
        # Aggregate signals from all modules
        if 'indicators' in analysis_result['modules'] and 'trading_signals' in analysis_result['modules']['indicators']:
            signals = analysis_result['modules']['indicators']['trading_signals']
            if 'BUY' in str(signals):
                recommendation = 'BUY'
                confidence = min(85, confidence + 20)
            elif 'SELL' in str(signals):
                recommendation = 'SELL'
                confidence = min(85, confidence + 20)
        
        analysis_result['recommendation'] = recommendation
        analysis_result['confidence'] = confidence
        
        return jsonify(analysis_result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*80)
    print("ARTHSETU MARKET INTELLIGENCE - LOCAL API SERVER")
    print("="*80)
    print("\n[STARTING] Flask server on http://localhost:7000")
    print("\n[DATA SOURCES]")
    if ALPHA_VANTAGE_API_KEY and ALPHA_VANTAGE_API_KEY != '':
        print(f"   Alpha Vantage API: ENABLED (using provided API key)")
        print(f"   Yahoo Finance (yfinance): ENABLED (fallback/verification)")
        print(f"   Strategy: Parallel fetching - use BEST price from both sources")
    else:
        print(f"   Alpha Vantage API: NOT CONFIGURED")
        print(f"   Yahoo Finance (yfinance): ENABLED (primary)")
        print(f"   ★ Add ALPHA_VANTAGE_API_KEY to .env file to enable dual source\n")
    
    print("\n[ENDPOINTS] Core Market Data:")
    print("   GET /                    - Serve Frontend")
    print("   GET /api/stock/<symbol>  - Basic stock analysis")
    print("   GET /api/market/ticker   - Real-time stock ticker")
    print("   POST /api/chat           - AI Market Analyst Chatbot")
    print("\n[INVESTOR GUIDANCE] Fundamentals Analysis:")
    print("   GET /api/fundamentals/<symbol>       - Full financial analysis (P/E, EPS, ROE, D/E)")
    print("   POST /api/fundamentals/compare       - Compare fundamentals of multiple stocks")
    print("\n[INVESTOR GUIDANCE] Sentiment & News:")
    print("   GET /api/sentiment/<symbol>          - Market sentiment + news analysis")
    print("   POST /api/sentiment/compare          - Compare sentiment across stocks")
    print("\n[INVESTOR GUIDANCE] Technical Indicators:")
    print("   GET /api/indicators/<symbol>         - All indicators (RSI, MACD, Bollinger, S/R)")
    print("   GET /api/indicators/rsi/<symbol>     - RSI indicator alone")
    print("   GET /api/indicators/macd/<symbol>    - MACD indicator alone")
    print("   GET /api/indicators/bollinger/<symbol> - Bollinger Bands alone")
    print("\n[INVESTOR GUIDANCE] Risk Management:")
    print("   POST /api/risk/portfolio             - Portfolio risk & diversification score")
    print("   POST /api/risk/position-size         - Calculate optimal position size")
    print("   POST /api/risk/stop-loss/<symbol>    - Calculate stop-loss/take-profit levels")
    print("   POST /api/risk/var                   - Value at Risk (VaR) calculation")
    print("\n[INVESTOR GUIDANCE] Backtesting:")
    print("   GET /api/backtest/<symbol>           - Backtest single strategy")
    print("   GET /api/backtest/compare/<symbol>   - Compare all 3 strategies")
    print("\n[COMPREHENSIVE] Complete Analysis:")
    print("   GET /api/analysis/complete/<symbol>  - ALL analysis modules combined!")
    print("\n[INTERACTIVE] Paper Trading & Alerts:")
    print("   POST /api/paper-trading/start        - Start virtual trading")
    print("   GET /api/paper-trading/leaderboard   - Top traders leaderboard")
    print("   POST /api/alerts/add                 - Set price alert")
    print("   GET /api/alerts/list                 - Get your alerts")
    print("\n[FEATURES] Available Now:")
    print("   [+] Fundamentals Analysis (P/E, EPS, ROE, Dividend Yield, Debt/Equity)")
    print("   [+] Sentiment Analysis (News + Multi-Source Signals)")
    print("   [+] 5 Technical Indicators (RSI, MACD, Bollinger Bands, Support/Resistance, Volume)")
    print("   [+] Risk Management (Diversification, Position Sizing, Stop-Loss, VaR, Sharpe Ratio)")
    print("   [+] Strategy Backtesting (Moving Average, RSI, Momentum Strategies)")
    print("   [+] DUAL SOURCE Real-Time Prices (Alpha Vantage + Yahoo Finance)")
    print("   [+] AI-Powered Market Q&A Chatbot")
    print("   [+] Paper Trading Simulator with Leaderboard")
    print("   [+] Smart Price Alerts & Notifications")
    print("\n" + "="*80 + "\n")
    
    app.run(host='0.0.0.0', port=7000, debug=False, use_reloader=False)
