"""
ArthaSetu Database Module - SQLite3 Backend
Stores user data, portfolio, trades, alerts
"""

import sqlite3
import json
from datetime import datetime
import os
from hashlib import sha256

DB_PATH = os.path.join(os.path.dirname(__file__), 'arthsetu.db')

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Portfolio table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                buy_price REAL NOT NULL,
                sector TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Paper trading table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS paper_trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                entry_price REAL NOT NULL,
                exit_price REAL,
                side TEXT,
                status TEXT DEFAULT 'OPEN',
                pnl REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Price alerts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                target_price REAL NOT NULL,
                alert_type TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        
        # Market cache table (for offline use)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS market_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT UNIQUE NOT NULL,
                price REAL NOT NULL,
                recommendation TEXT,
                sector TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def hash_password(password):
        """Hash password"""
        return sha256(password.encode()).hexdigest()
    
    def register_user(self, email, password, name):
        """Register new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, name)
                VALUES (?, ?, ?)
            ''', (email, password_hash, name))
            
            conn.commit()
            user_id = cursor.lastrowid
            conn.close()
            return {'status': 'success', 'user_id': user_id, 'message': 'User registered'}
        except sqlite3.IntegrityError:
            return {'status': 'error', 'message': 'Email already registered'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def login_user(self, email, password):
        """Verify user login"""
        conn = self.get_connection()
        cursor = conn.cursor()
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, name, email FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'status': 'success',
                'user_id': user[0],
                'name': user[1],
                'email': user[2]
            }
        return {'status': 'error', 'message': 'Invalid credentials'}
    
    def get_user(self, user_id):
        """Get user by ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, name FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None
    
    def add_portfolio_item(self, user_id, symbol, quantity, buy_price, sector='Other'):
        """Add stock to portfolio"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO portfolio (user_id, symbol, quantity, buy_price, sector)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, symbol, quantity, buy_price, sector))
            
            conn.commit()
            conn.close()
            return {'status': 'success', 'message': 'Stock added'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_portfolio(self, user_id):
        """Get user's portfolio"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, symbol, quantity, buy_price, sector, created_at
            FROM portfolio WHERE user_id = ?
        ''', (user_id,))
        
        items = cursor.fetchall()
        conn.close()
        return [dict(item) for item in items]
    
    def add_paper_trade(self, user_id, symbol, quantity, entry_price, side='LONG'):
        """Record paper trade"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO paper_trades (user_id, symbol, quantity, entry_price, side)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, symbol, quantity, entry_price, side))
            
            conn.commit()
            trade_id = cursor.lastrowid
            conn.close()
            return {'status': 'success', 'trade_id': trade_id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_paper_trades(self, user_id):
        """Get user's paper trades"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, symbol, quantity, entry_price, exit_price, side, status, pnl, created_at
            FROM paper_trades WHERE user_id = ? ORDER BY created_at DESC
        ''', (user_id,))
        
        trades = cursor.fetchall()
        conn.close()
        return [dict(trade) for trade in trades]
    
    def add_price_alert(self, user_id, symbol, target_price, alert_type='ABOVE'):
        """Add price alert"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO price_alerts (user_id, symbol, target_price, alert_type)
                VALUES (?, ?, ?, ?)
            ''', (user_id, symbol, target_price, alert_type))
            
            conn.commit()
            conn.close()
            return {'status': 'success', 'message': 'Alert created'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_price_alerts(self, user_id):
        """Get user's price alerts"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, symbol, target_price, alert_type, is_active, created_at
            FROM price_alerts WHERE user_id = ? AND is_active = 1
        ''', (user_id,))
        
        alerts = cursor.fetchall()
        conn.close()
        return [dict(alert) for alert in alerts]
    
    def update_market_cache(self, symbol, price, recommendation, sector):
        """Update market data cache"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO market_cache (symbol, price, recommendation, sector)
                VALUES (?, ?, ?, ?)
            ''', (symbol, price, recommendation, sector))
            
            conn.commit()
            conn.close()
            return {'status': 'success'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_market_cache(self, symbol):
        """Get cached market data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT symbol, price, recommendation, sector, updated_at
            FROM market_cache WHERE symbol = ?
        ''', (symbol,))
        
        result = cursor.fetchone()
        conn.close()
        return dict(result) if result else None

# Initialize database
db = Database()
