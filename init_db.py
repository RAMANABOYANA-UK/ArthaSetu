#!/usr/bin/env python
"""Initialize demo users in database"""

from database import db

# Add demo users
demo1 = db.register_user('demo@arthsetu.com', 'demo123', 'Demo User')
demo2 = db.register_user('test@arthsetu.com', 'test123', 'Test User')

print("Demo users created:")
print(f"  Email: demo@arthsetu.com | Password: demo123 | Status: {demo1['status']}")
print(f"  Email: test@arthsetu.com | Password: test123 | Status: {demo2['status']}")

# Add sample portfolio
if demo1['status'] == 'success':
    user_id = demo1['user_id']
    stocks = [
        ('TCS.NS', 10, 3500, 'IT'),
        ('INFY.NS', 15, 1400, 'IT'),
        ('RELIANCE.NS', 5, 2400, 'Energy'),
        ('ITC.NS', 20, 420, 'FMCG'),
    ]
    for symbol, qty, price, sector in stocks:
        db.add_portfolio_item(user_id, symbol, qty, price, sector)
    print("\n✅ Sample portfolio added to demo@arthsetu.com")

print("\n📊 Database ready for use!")
