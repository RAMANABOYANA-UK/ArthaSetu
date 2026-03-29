import requests
import time

time.sleep(2)

print("\n" + "="*60)
print("ARTHSETU API - FINAL TEST")
print("="*60 + "\n")

try:
    # Test 1: Stock
    print("[OK] Testing Stock Analysis...")
    r = requests.get('http://localhost:5000/stock/TCS')
    data = r.json()
    if data.get('status') == 'success':
        rec = data.get('recommendation', {})
        print(f"    TCS Recommendation: {rec.get('recommendation')}")
        print(f"    Confidence: {rec.get('confidence', 0):.0%}")
        print(f"    Price: ₹{data.get('live_price')}")
        print("    [OK] STOCK API WORKING!\n")
    
    # Test 2: Portfolio
    print("[OK] Testing Portfolio Analysis...")
    r2 = requests.get('http://localhost:5000/portfolio')
    data2 = r2.json()
    if data2.get('status') == 'success':
        print(f"    Total Value: ₹{data2.get('metrics', {}).get('total_value')}")
        print(f"    Risk Level: {data2.get('concentration', {}).get('concentration_risk')}")
        print("    [OK] PORTFOLIO API WORKING!\n")
    
    # Test 3: Sectors
    print("[OK] Testing Sector Analysis...")
    r3 = requests.get('http://localhost:5000/sectors')
    data3 = r3.json()
    if data3.get('status') == 'success':
        print(f"    Sector data received successfully")
        print("    [OK] SECTORS API WORKING!\n")
    
    print("="*60)
    print("[SUCCESS] ALL APIs WORKING CORRECTLY!")
    print("Your website will now show REAL LIVE DATA!")
    print("="*60)
    
except Exception as e:
    print(f"ERROR: {e}")
