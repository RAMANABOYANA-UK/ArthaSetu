# Alpha Vantage Integration Setup Guide

## ✅ What's Done

Your API server is now configured to fetch stock prices from **BOTH sources in parallel**:
- **Alpha Vantage API** - Enterprise-grade real-time data
- **Yahoo Finance (yfinance)** - Reliable fallback source

## 📋 Setup Instructions

### Step 1: Get Your Alpha Vantage API Key
1. Visit: https://www.alphavantage.co/
2. Click "GET FREE API KEY"
3. Enter your email and click "Get Free API Key"
4. Copy your API key (looks like: `ABC123XYZ...`)

### Step 2: Add API Key to .env File
Edit the `.env` file in your project root:
```
ALPHA_VANTAGE_API_KEY=your_api_key_here
DATA_SOURCE_PRIORITY=BOTH
FLASK_ENV=production
FLASK_PORT=7000
```

Replace `your_api_key_here` with your actual API key from Step 1.

### Step 3: Start the Server
```bash
cd D:\ArthaSetu
.\.venv\Scripts\Activate.ps1
python api_server.py
```

## 🔄 How Parallel Fetching Works

When you request a stock price:

```
REQUEST: GET /api/stock/TCS.NS
         ↓
    PARALLEL FETCH
    ├─→ Alpha Vantage (Thread 1)
    └─→ Yahoo Finance (Thread 2)
         ↓
    COMPARISON LOGIC
    ├─ If both succeed AND prices match → Use average
    ├─ If prices differ >5% → Use yfinance (more frequent updates)
    ├─ If only one succeeds → Use that source
    └─ If both fail → Use fallback mock data
         ↓
RESPONSE: {
    "live_price": 2389.80,
    "price_source": "Dual Source (AV + YF Average)",
    "alt_price": null,
    "recommendation": "BUY",
    "confidence": 78
}
```

## 📊 Response Format (After Integration)

### /api/stock/<symbol> Endpoint:
```json
{
    "status": "success",
    "live_price": 2389.80,
    "price_source": "Alpha Vantage",
    "alt_price": 2388.50,
    "recommendation": "BUY",
    "confidence": 78,
    "sector": "IT",
    "sentiment": "BULLISH",
    "verified": true
}
```

Fields:
- `live_price` - The main price to use
- `price_source` - Which source provided this price
- `alt_price` - Alternative price from other source (for comparison)
- `verified` - true if live data, false if mock

## 🧪 Test the Integration

### Test 1: Single Stock
```bash
curl http://localhost:7000/api/stock/TCS.NS
```

Expected: Real price from Alpha Vantage or yfinance

### Test 2: Multiple Stocks
```bash
curl http://localhost:7000/api/stock/INFY.NS
curl http://localhost:7000/api/stock/RELIANCE.NS
```

### Test 3: Chatbot with Real Data
```bash
curl -X POST http://localhost:7000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "which stocks to buy?"}'
```

Expected: Response with actual prices from dual sources

### Test 4: Real-time Ticker
```bash
curl http://localhost:7000/api/chat
```

Expected: Ticker with prices and data sources

## ⚡ Alpha Vantage API Limits

**Free Tier:**
- 5 requests per minute
- 500 requests per day
- Intraday data: Most recent ~100 days

**Rate Limiting:**
If you exceed 5 req/min:
- Alpha Vantage will return error
- Server automatically falls back to yfinance
- No service interruption

**Solution for Heavy Use:**
- Upgrade to premium API key (paid tier)
- Implement request queueing
- Use 60-day data cache

## 🔍 Debug Mode

To see which source is being used:

1. Check server console output:
```
[PRICE COMPARISON] TCS.NS: AV=2389.80, YF=2388.50 (diff: 0.05%)
```

2. Check response `price_source` field:
   - `Alpha Vantage` - Using AV only
   - `Yahoo Finance` - Using yfinance only
   - `Dual Source (AV + YF Average)` - Using both (prices match)
   - `Fallback Mock Data` - Both sources failed

3. Monitor logs while running:
```bash
python api_server.py 2>&1 | Tee-Object -FilePath server.log
```

## 📝 Configuration Options

In `.env` file, you can set:

```env
# Your Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=your_key_here

# Data source priority (BOTH / ALPHA_VANTAGE / YFINANCE)
DATA_SOURCE_PRIORITY=BOTH

# Flask configuration
FLASK_ENV=production
FLASK_PORT=7000
```

## ✅ Verification Checklist

- [ ] Alpha Vantage API key obtained from website
- [ ] API key added to `.env` file
- [ ] Python dependencies installed (`python-dotenv` installed)
- [ ] Server starts without errors
- [ ] `/api/stock/<symbol>` returns real prices
- [ ] `price_source` field shows data origin
- [ ] Chatbot responds with actual stock prices

## 🎯 Next Steps

Once verified:
1. Open browser: http://localhost:7000
2. Navigate to "Stocks" section
3. Search for a stock (e.g., "TCS")
4. See real price from Alpha Vantage + yfinance comparison
5. Chat with the AI about stocks - it now uses real dual-source data!

## 📞 Troubleshooting

**"No module named 'dotenv'"**
```bash
pip install python-dotenv
```

**"Alpha Vantage rate limit exceeded"**
- Wait a minute and retry
- Server falls back to yfinance
- Upgrade to paid API key for higher limits

**"All data sources failed"**
- Check internet connection
- Verify API key in .env file
- Server uses mock data as final fallback

**Server won't start**
```bash
python api_server.py 2>&1  # Check full error
python -m py_compile api_server.py  # Check syntax
```

---

## 🚀 Ready to Integration!

Your infrastructure is set up. Just add your API key and you're done!

**When you provide your API key, the system will:**
✅ Load it from .env securely
✅ Start parallel fetching on each request
✅ Compare prices in real-time
✅ Show verification status in responses
✅ Provide dual-source confidence

**Questions?** Check the logs or test endpoints individually.
