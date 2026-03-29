import requests
import json

# Login  
url = 'http://localhost:7000/api/auth/login'
data = {'email': 'test@example.com', 'password': 'password123'}
session = requests.Session()
response = session.post(url, json=data)
print("=== Login Response ===")
print(json.loads(response.text))
print()

# Fetch fundamentals (should now work with TCS)
url = 'http://localhost:7000/api/fundamentals/TCS'
response = session.get(url)
print("=== Fundamentals (TCS) - FIXED ===")
resp_json = json.loads(response.text)
print(json.dumps(resp_json, indent=2))
print()

# Fetch recommendations  
url = 'http://localhost:7000/api/market/recommendations'
response = session.get(url)
print("=== Market Recommendations ===")
resp_json = json.loads(response.text)
print(f"Status: {resp_json.get('status')}")
print(f"Total Recommendations: {len(resp_json.get('recommendations', []))}")
for rec in resp_json.get('recommendations', [])[:2]:
    print(f"  - {rec['symbol']}: {rec['recommendation']} (Confidence: {rec['confidence']}%)")
print()

# Fetch indicators
url = 'http://localhost:7000/api/indicators/TCS'
response = session.get(url)
print("=== Indicators (TCS) ===")
resp_json = json.loads(response.text)
print(f"Status: {resp_json.get('status')}")
if 'technical_indicators' in resp_json:
    print(f"RSI: {resp_json['technical_indicators'].get('rsi', {}).get('value', 'N/A')}")
    print(f"MACD: {resp_json['technical_indicators'].get('macd', {}).get('value', 'N/A')}")
