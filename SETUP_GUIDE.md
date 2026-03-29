# ArthaSetu Dashboard - Setup & Installation Guide

## 🚀 Quick Start (Clone & Run)

### **Option 1: Clone from GitHub (HTTPS)**

```bash
# Clone the repository
git clone https://github.com/RAMANABOYANA-UK/ArthaSetu.git
cd ArthaSetu

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the API server
python api_server.py

# Open in browser
# Dashboard: http://localhost:7000
```

### **Option 2: Clone from GitHub (SSH)**

```bash
# If you have SSH key configured
git clone git@github.com:RAMANABOYANA-UK/ArthaSetu.git
cd ArthaSetu

# Follow same steps as above
```

### **Option 3: Direct Download (No Git)**

1. Go to: https://github.com/RAMANABOYANA-UK/ArthaSetu
2. Click **"Code"** → **"Download ZIP"**
3. Extract the ZIP file
4. Follow the installation steps above

---

## 🔧 System Requirements

- **Python**: 3.8 or higher
- **Node.js**: Optional (for PWA features)
- **RAM**: 2GB+ recommended
- **Disk Space**: 500MB

---

## ⚙️ Installation Steps

### 1. **Clone Repository**
```bash
git clone https://github.com/RAMANABOYANA-UK/ArthaSetu.git
cd ArthaSetu
```

### 2. **Setup Python Virtual Environment**
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Mac/Linux
source .venv/bin/activate
```

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Configure Environment**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your API keys (optional but recommended)
# - ALPHA_VANTAGE_API_KEY (for real stock prices)
# - Other API keys if needed
```

### 5. **Initialize Database**
```bash
python init_db.py
```

### 6. **Start the Server**
```bash
python api_server.py
```

You should see:
```
================================================================================
ARTHSETU MARKET INTELLIGENCE - LOCAL API SERVER
================================================================================
[STARTING] Flask server on http://localhost:7000
 * Running on http://127.0.0.1:7000
Press CTRL+C to quit
```

### 7. **Open Dashboard**
Open browser and go to: **http://localhost:7000**

---

## 📋 Features Available

### Dashboard
- Investment Overview with real-time metrics
- Top Stock Recommendations
- Market Sentiment Analysis
- Portfolio Performance Charts

### Stocks Section
- Search and analyze any stock symbol
- Comprehensive analysis with:
  - Fundamental Analysis (P/E, ROE, Dividend)
  - News Sentiment (bullish/bearish indicators)
  - Technical Indicators (RSI, MACD, etc.)
  - Risk Assessment
  - Backtesting Results

### Markets Section  
- Market Sentiment (6 indicators)
  - Market Breadth
  - Volatility Index (VIX)
  - Market Momentum
  - RSI
  - FII Investment
  - P/E Ratio
- Market Performance (5 indices)
  - NIFTY 50
  - SENSEX
  - NIFTY BANK
  - IT INDEX
  - PHARMA INDEX

### Top Recommendations
- 13 carefully selected stocks across 7 sectors
- Sector distribution analysis
- Real-time price updates

### Portfolio
- Add/remove stocks
- Track holdings
- Real-time valuation

---

## 🔑 API Endpoints

### Public Endpoints
```
GET  /                               - Dashboard
GET  /api/health                     - Server health check
GET  /api/market/recommendations     - Get 13 stock recommendations
GET  /api/market/sentiment           - Get market sentiment (6 indicators)
GET  /api/market/performance         - Get market indices (5 major)
GET  /api/analysis/complete/<symbol> - Complete stock analysis
```

### Authentication Endpoints
```
POST /api/auth/register    - Register new user
POST /api/auth/login       - Login user
POST /api/auth/logout      - Logout user
GET  /api/auth/me          - Get current user info
```

### Portfolio Endpoints
```
GET  /api/portfolio/items  - Get portfolio holdings
POST /api/portfolio/add    - Add stock to portfolio
```

---

## 🔐 Authentication

### Default Test Credentials
```
Email: test@arthsetu.com
Password: test123
```

### Create New Account
1. On the login page, click "Sign Up"
2. Enter email and password
3. Click "Create Account"
4. You'll be logged in immediately

---

## 📊 Stock Recommendations (13 Total)

| Symbol | Sector | Recommendation | Confidence |
|--------|--------|----------------|------------|
| TCS | IT | BUY | 78% |
| INFY | IT | BUY | 82% |
| WIPRO | IT | BUY | 75% |
| RELIANCE | Energy | HOLD | 65% |
| ITC | FMCG | SELL | 72% |
| BAJAJFINSV | Finance | BUY | 80% |
| HDFCBANK | Banking | HOLD | 68% |
| AXISBANK | Banking | BUY | 76% |
| MARUTI | Auto | HOLD | 62% |
| LT | Engineering | BUY | 79% |
| NESTLEIND | FMCG | HOLD | 70% |
| PHARMACIE | Pharma | BUY | 81% |
| GICRE | Insurance | SELL | 71% |

---

## ⚡ Performance Tips

1. **Faster Stock Analysis**: Analysis results are cached for 1.5 seconds
2. **Parallel Loading**: Multiple data sources load simultaneously
3. **Offline Support**: PWA caches data for offline viewing
4. **Local Database**: SQLite database for portfolio persistence

---

## 🐛 Troubleshooting

### "Port 7000 already in use"
```bash
# Kill existing process
# Windows:
netstat -ano | findstr :7000
taskkill /PID <PID> /F

# Mac/Linux:
lsof -i :7000
kill -9 <PID>
```

### "Module not found" errors
```bash
# Ensure virtual environment is activated
# Then reinstall dependencies
pip install --upgrade -r requirements.txt
```

### "Database locked" error
```bash
# Delete old database and reinitialize
rm arthsetu.db
python init_db.py
```

### "API returns empty data"
```bash
# Some features require Alpha Vantage API key
# The app uses mock data by default
# To use real data, add API key to .env
ALPHA_VANTAGE_API_KEY=your_key_here
```

---

## 📱 Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

---

## 🔄 Git Commands

### Update Your Local Copy
```bash
git pull origin master
```

### Make Changes
```bash
git add .
git commit -m "Your message"
git push origin master
```

### Check Status
```bash
git status
git log --oneline
```

---

## 📚 Documentation Files

- `README.md` - Project overview
- `START_HERE.md` - Getting started guide
- `IMPLEMENTATION_SUMMARY.md` - What was implemented
- `PLATFORM_READY.md` - Production readiness checklist
- `API_REFERENCE.py` - API documentation

---

## 🆘 Need Help?

1. Check the troubleshooting section above
2. Review documentation files in the repo
3. Check the browser console (F12) for JavaScript errors
4. Check server logs (terminal output)

---

## 📝 License

This project is open source. See LICENSE file for details.

---

**Version**: 2.0  
**Last Updated**: March 30, 2026  
**Status**: ✅ Production Ready
