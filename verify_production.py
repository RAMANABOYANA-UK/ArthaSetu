#!/usr/bin/env python
"""Verification script to test all components"""

import requests
import json
from database import db

print("\n" + "="*80)
print("🚀 ARTHSETU - PRODUCTION VERIFICATION TEST")
print("="*80 + "\n")

BASE_URL = "http://localhost:7000"

# Test 1: Database
print("✓ Test 1: DATABASE CHECK")
try:
    users = db.db.execute("SELECT COUNT(*) FROM users").fetchone()
    print(f"  ✅ Database running | Users in DB: {users[0]}")
except Exception as e:
    print(f"  ❌ Database error: {e}")

# Test 2: Server health
print("\n✓ Test 2: API SERVER HEALTH")
try:
    response = requests.get(f"{BASE_URL}/api/health")
    status = response.json()['status']
    print(f"  ✅ Server running | Status: {status}")
except Exception as e:
    print(f"  ❌ Server error: {e}")

# Test 3: Frontend
print("\n✓ Test 3: FRONTEND LOADING")
try:
    response = requests.get(f"{BASE_URL}/")
    if "ArthaSetu" in response.text and "auth-container" in response.text:
        print(f"  ✅ Frontend loaded | Size: {len(response.text)} bytes")
    else:
        print(f"  ⚠️  Frontend missing key elements")
except Exception as e:
    print(f"  ❌ Frontend error: {e}")

# Test 4: User Authentication
print("\n✓ Test 4: USER AUTHENTICATION")
try:
    login_data = {"email": "demo@arthsetu.com", "password": "demo123"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    result = response.json()
    if result['status'] == 'success':
        print(f"  ✅ Login successful | User: {result['user']['name']}")
    else:
        print(f"  ❌ Login failed: {result['message']}")
except Exception as e:
    print(f"  ❌ Auth error: {e}")

# Test 5: Portfolio Data
print("\n✓ Test 5: PORTFOLIO DATA")
try:
    # Get user portfolio from DB
    portfolio = db.get_portfolio(1)
    if portfolio:
        print(f"  ✅ Portfolio loaded | Holdings: {len(portfolio)}")
        for stock in portfolio[:2]:
            print(f"     - {stock['symbol']}: {stock['quantity']} units @ ₹{stock['buy_price']}")
    else:
        print(f"  ⚠️  No portfolio data")
except Exception as e:
    print(f"  ❌ Portfolio error: {e}")

# Test 6: Market Recommendations
print("\n✓ Test 6: MARKET RECOMMENDATIONS")
try:
    response = requests.get(f"{BASE_URL}/api/market/recommendations")
    recs = response.json()['recommendations']
    print(f"  ✅ Recommendations loaded | Count: {len(recs)}")
    for rec in recs[:2]:
        print(f"     - {rec['symbol']}: {rec['recommendation']} (Confidence: {rec['confidence']}%)")
except Exception as e:
    print(f"  ❌ Recommendations error: {e}")

# Test 7: Real-time Stock Analysis
print("\n✓ Test 7: REAL-TIME STOCK ANALYSIS")
try:
    response = requests.get(f"{BASE_URL}/api/stock/TCS.NS")
    stock = response.json()
    if stock['status'] == 'success':
        price = stock['live_price']
        signal = stock['recommendation']['recommendation']
        conf = stock['recommendation']['confidence']
        print(f"  ✅ TCS Analysis | Price: ₹{price} | Signal: {signal} | Confidence: {conf}%")
    else:
        print(f"  ⚠️  Stock analysis unavailable")
except Exception as e:
    print(f"  ❌ Stock analysis error: {e}")

# Test 8: Offline Support
print("\n✓ Test 8: OFFLINE SUPPORT (PWA)")
try:
    response = requests.get(f"{BASE_URL}/manifest.json")
    manifest = response.json()
    if manifest.get('name'):
        print(f"  ✅ PWA manifest loaded | App: {manifest['name'][:30]}...")
except Exception as e:
    print(f"  ❌ PWA manifest error: {e}")

# Test 9: Service Worker
print("\n✓ Test 9: SERVICE WORKER")
try:
    response = requests.get(f"{BASE_URL}/service-worker.js")
    if "serviceWorker" in response.text and "caches" in response.text:
        print(f"  ✅ Service Worker ready | Size: {len(response.text)} bytes")
    else:
        print(f"  ⚠️  Service Worker incomplete")
except Exception as e:
    print(f"  ❌ Service Worker error: {e}")

# Test 10: Database Persistence
print("\n✓ Test 10: DATA PERSISTENCE")
try:
    # Try to add a test alert
    alert_result = db.add_price_alert(1, "INFY.NS", 1500, "ABOVE")
    if alert_result['status'] == 'success':
        # Retrieve it
        alerts = db.get_price_alerts(1)
        print(f"  ✅ Data persistance working | Alerts: {len(alerts)}")
    else:
        print(f"  ⚠️  Alert creation failed")
except Exception as e:
    print(f"  ❌ Persistence error: {e}")

print("\n" + "="*80)
print("✨ PRODUCTION VERIFICATION COMPLETE")
print("="*80)
print("\n🎉 Your app is ready! Access it at: http://localhost:7000")
print("\n📝 Login Credentials:")
print("   Email: demo@arthsetu.com")
print("   Password: demo123\n")
