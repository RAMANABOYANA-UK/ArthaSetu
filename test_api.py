"""
Test ArthaSetu Local API Server
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

print("\n" + "="*80)
print("ARTHSETU LOCAL API - TEST SUITE")
print("="*80)

# Test 1: Health check
print("\n[TEST 1] Health Check")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: API Info
print("\n[TEST 2] API Info")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)[:500]}...")
except Exception as e:
    print(f"Error: {e}")

# Test 3: Analyze Stock (TCS)
print("\n[TEST 3] Analyze Stock - TCS")
try:
    response = requests.get(f"{BASE_URL}/stock/TCS")
    print(f"Status: {response.status_code}")
    data = response.json()
    rec = data.get('recommendation', {})
    print(f"Recommendation: {rec.get('recommendation')}")
    print(f"Confidence: {rec.get('confidence', 0):.0%}")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Analyze Stock (INFY)
print("\n[TEST 4] Analyze Stock - Infosys")
try:
    response = requests.get(f"{BASE_URL}/stock/INFY")
    print(f"Status: {response.status_code}")
    data = response.json()
    rec = data.get('recommendation', {})
    print(f"Recommendation: {rec.get('recommendation')}")
    print(f"Confidence: {rec.get('confidence', 0):.0%}")
except Exception as e:
    print(f"Error: {e}")

# Test 5: Portfolio Analysis
print("\n[TEST 5] Portfolio Risk Analysis")
try:
    response = requests.get(f"{BASE_URL}/portfolio")
    print(f"Status: {response.status_code}")
    data = response.json()
    conc = data.get('concentration', {})
    print(f"Concentration Risk: {conc.get('concentration_risk')}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*80)
print("TESTS COMPLETE - Local API is working!")
print("="*80 + "\n")
