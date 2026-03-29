#!/usr/bin/env python3
"""
ArthaSetu - Start Real-Time Investment Intelligence Platform
Launches Flask API with user authentication & real-time stock data on localhost:5000
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_header():
    print(f"\n{BLUE}{'='*60}")
    print(f"   ArthaSetu - Stock Investment Intelligence Platform")
    print(f"   Real-Time Analysis with User Authentication")
    print(f"{'='*60}{RESET}\n")

def check_requirements():
    """Check if required packages are installed"""
    required = ['flask', 'pandas', 'yfinance', 'ta', 'vaderSentiment']
    missing = []
    
    for package in required:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"{YELLOW}[!] Missing packages: {', '.join(missing)}")
        print(f"[*] Installing dependencies...{RESET}")
        subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing, check=False)
    
    # Check for flask-cors specifically
    try:
        __import__('flask_cors')
    except ImportError:
        print(f"{YELLOW}[*] Installing flask-cors for API access...{RESET}")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'flask-cors'], check=False)

def print_startup_info():
    """Print startup information"""
    print(f"{GREEN}[OK]{RESET} Starting Flask API Server...")
    print(f"{GREEN}[OK]{RESET} Loading Multi-Agent Orchestrator...")
    print(f"{GREEN}[OK]{RESET} Initializing Real-Time Data Fetcher...")
    print(f"\n{BLUE}[*] SERVER DETAILS:{RESET}")
    print(f"    API Base URL: http://localhost:5000/api")
    print(f"    Frontend: Open http://localhost:5000 in browser")
    print(f"\n{BLUE}[*] DEMO LOGIN:{RESET}")
    print(f"    Email: demo@arthsetu.com")
    print(f"    Password: demo123")
    print(f"\n{BLUE}[*] FEATURES:{RESET}")
    print(f"    • Real-time stock analysis with multi-agent AI")
    print(f"    • User authentication & portfolio management")
    print(f"    • Live price data via yfinance")
    print(f"    • Technical indicators (RSI, MACD, Bollinger Bands)")
    print(f"    • Sentiment analysis on market news")
    print(f"    • Sector rotation analysis")
    print(f"\n{YELLOW}Press Ctrl+C to stop server{RESET}\n")

if __name__ == "__main__":
    print_header()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print(f"{YELLOW}[!] Python 3.8+ required (you have {sys.version_info.major}.{sys.version_info.minor}){RESET}")
        sys.exit(1)
    
    # Check and install requirements
    print(f"{YELLOW}[*] Checking dependencies...{RESET}")
    check_requirements()
    
    # Import Flask app
    try:
        from api_enhanced import app
    except ImportError as e:
        print(f"{YELLOW}[!] Error importing api_enhanced.py: {e}{RESET}")
        sys.exit(1)
    
    # Try to serve index.html at root
    @app.route('/')
    def serve_index():
        current_dir = Path(__file__).parent
        with open(current_dir / 'index.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    print_startup_info()
    
    # Start Flask server
    try:
        app.run(
            host='localhost',
            port=5000,
            debug=True,
            use_reloader=False,
            threaded=True
        )
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Server stopped by user{RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{YELLOW}[!] Error: {e}{RESET}")
        sys.exit(1)
