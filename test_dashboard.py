import requests
import json

# Login
url = 'http://localhost:7000/api/auth/login'
data = {'email': 'test@example.com', 'password': 'password123'}
session = requests.Session()
response = session.post(url, json=data)
print("=== Login Response ===")
print(response.text)
print()

# Add a stock to portfolio
url = 'http://localhost:7000/api/portfolio/add'
data = {'symbol': 'TCS', 'quantity': 10, 'price': 3500, 'sector': 'IT'}
response = session.post(url, json=data)
print("=== Add Stock Response ===")
print(response.text)
print()

# Fetch portfolio items
url = 'http://localhost:7000/api/portfolio/items'
response = session.get(url)
print("=== Portfolio Items ===")
print(response.text)
print()

# Fetch live stock price
url = 'http://localhost:7000/api/stock/TCS'
response = session.get(url)
print("=== Stock Price (TCS) ===")
print(response.text)
print()

# Fetch recommendations
url = 'http://localhost:7000/api/market/recommendations'
response = session.get(url)
print("=== Market Recommendations ===")
print(response.text)
print()

# Fetch fundamentals
url = 'http://localhost:7000/api/fundamentals/TCS'
response = session.get(url)
print("=== Fundamentals (TCS) ===")
print(response.text)
