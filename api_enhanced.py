"""
ArthaSetu - Enhanced API with User Management & Real-Time Data
"""

from flask import Flask, jsonify, request, session, send_file
from flask_cors import CORS
from simple_orchestrator import SimpleMarketIntelligenceOrchestrator
from demo_data import SAMPLE_PORTFOLIO
import json
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'arthsetu_secret_key_2026'
CORS(app)  # Enable CORS for all routes
orchestrator = SimpleMarketIntelligenceOrchestrator()

# In-memory user database (replace with real DB in production)
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

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()}), 200

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register new user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        if email in USERS_DB:
            return jsonify({'status': 'error', 'message': 'User already exists'}), 400
        
        USERS_DB[email] = {
            'password': password,
            'name': name,
            'portfolio': []
        }
        
        session['user'] = email
        return jsonify({
            'status': 'success',
            'message': 'Registration successful',
            'user': {'email': email, 'name': name}
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        if email not in USERS_DB or USERS_DB[email]['password'] != password:
            return jsonify({'status': 'error', 'message': 'Invalid credentials'}), 401
        
        session['user'] = email
        user = USERS_DB[email]
        
        return jsonify({
            'status': 'success',
            'message': 'Login successful',
            'user': {'email': email, 'name': user['name']}
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Logout user"""
    session.pop('user', None)
    return jsonify({'status': 'success', 'message': 'Logged out'}), 200

@app.route('/api/auth/me', methods=['GET'])
def get_user():
    """Get current user"""
    if 'user' not in session:
        return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
    
    email = session['user']
    user = USERS_DB.get(email, {})
    
    return jsonify({
        'status': 'success',
        'user': {
            'email': email,
            'name': user.get('name'),
            'portfolio': user.get('portfolio', [])
        }
    }), 200

@app.route('/api/stock/<symbol>', methods=['GET'])
def analyze_stock(symbol):
    """Analyze stock for buy signal"""
    try:
        result = orchestrator.analyze_stock_for_buy(symbol.upper())
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/portfolio', methods=['GET'])
def analyze_portfolio():
    """Analyze user portfolio"""
    try:
        if 'user' not in session:
            portfolio = SAMPLE_PORTFOLIO
        else:
            user_portfolio = USERS_DB[session['user']].get('portfolio', [])
            portfolio = [
                {
                    'symbol': p['symbol'],
                    'sector': p['sector'],
                    'quantity': p['quantity'],
                    'current_price': p['buy_price']
                }
                for p in user_portfolio
            ]
        
        result = orchestrator.analyze_portfolio_risk(portfolio)
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/sectors', methods=['GET'])
def analyze_sectors():
    """Analyze sector rotation"""
    try:
        result = orchestrator.analyze_sector_rotation()
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    """Add stock to user portfolio"""
    try:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
        
        data = request.json
        email = session['user']
        
        stock = {
            'symbol': data.get('symbol'),
            'quantity': data.get('quantity', 1),
            'buy_price': data.get('price', 0),
            'sector': data.get('sector', 'Other')
        }
        
        USERS_DB[email]['portfolio'].append(stock)
        
        return jsonify({
            'status': 'success',
            'message': 'Stock added to portfolio',
            'stock': stock
        }), 201
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/portfolio/items', methods=['GET'])
def get_portfolio_items():
    """Get user portfolio items"""
    try:
        if 'user' not in session:
            return jsonify({'status': 'error', 'message': 'Not authenticated'}), 401
        
        email = session['user']
        portfolio = USERS_DB[email].get('portfolio', [])
        
        return jsonify({
            'status': 'success',
            'portfolio': portfolio
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/api/market/recommendations', methods=['GET'])
def get_recommendations():
    """Get top stock recommendations"""
    try:
        recommendations = [
            {'symbol': 'TCS', 'recommendation': 'BUY', 'confidence': 95, 'price': 2389, 'sentiment': 'BULLISH'},
            {'symbol': 'INFY', 'recommendation': 'BUY', 'confidence': 87, 'price': 1269, 'sentiment': 'BULLISH'},
            {'symbol': 'RELIANCE', 'recommendation': 'HOLD', 'confidence': 65, 'price': 2600, 'sentiment': 'NEUTRAL'},
            {'symbol': 'HDFC', 'recommendation': 'SELL', 'confidence': 72, 'price': 2400, 'sentiment': 'BEARISH'},
        ]
        
        return jsonify({
            'status': 'success',
            'recommendations': recommendations,
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/')
def serve_frontend():
    """Serve the main HTML page"""
    try:
        index_path = os.path.join(os.path.dirname(__file__), 'index.html')
        with open(index_path, 'r', encoding='utf-8') as f:
            return f.read(), 200, {'Content-Type': 'text/html; charset=utf-8'}
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Frontend error: {str(e)}'}), 404

if __name__ == '__main__':
    print("\n" + "="*80)
    print("ARTHSETU MARKET INTELLIGENCE - ENHANCED API WITH USER MANAGEMENT")
    print("="*80)
    print("\n🚀 Starting Enhanced Flask server on http://localhost:5000")
    print("\n📊 Available endpoints:")
    print("   Auth:")
    print("     POST /api/auth/register    - User registration")
    print("     POST /api/auth/login       - User login")
    print("     POST /api/auth/logout      - User logout")
    print("     GET  /api/auth/me          - Get current user")
    print("\n   Market Data:")
    print("     GET  /api/stock/<symbol>   - Analyze stock")
    print("     GET  /api/portfolio        - Portfolio analysis")
    print("     GET  /api/sectors          - Sector rotation")
    print("\n   Portfolio Management:")
    print("     GET  /api/portfolio/items  - Get portfolio items")
    print("     POST /api/portfolio/add    - Add stock to portfolio")
    print("\n   Market Intelligence:")
    print("     GET  /api/market/recommendations - Top recommendations")
    print("     GET  /api/health           - Health check")
    print("\n" + "="*80 + "\n")
    
    app.run(host='localhost', port=5000, debug=True, use_reloader=False)
