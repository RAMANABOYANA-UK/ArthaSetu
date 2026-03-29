# 🎯 ArthaSetu - Investment Intelligence Dashboard

**Real-time stock analysis, market sentiment, and investment recommendations for Indian markets.**

![Python](https://img.shields.io/badge/Python-3.8+-blue?style=flat-square)
![Flask](https://img.shields.io/badge/Flask-Latest-green?style=flat-square)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/RAMANABOYANA-UK/ArthaSetu.git
cd ArthaSetu
python -m venv .venv
.venv\Scripts\activate  # Windows
```

### 2. Install & Run
```bash
pip install -r requirements.txt
python api_server.py
```

Open: **http://localhost:7000**

---

## ✨ Features

- **13 Stock Recommendations** - BUY/SELL/HOLD signals across 7 sectors
- **Market Sentiment** - 6 real-time indicators (Breadth, VIX, Momentum, RSI, FII, P/E)
- **Market Indices** - NIFTY 50, SENSEX, NIFTY BANK, IT INDEX, PHARMA INDEX
- **Stock Analysis** - Fundamentals, sentiment, technical indicators, risk metrics
- **Portfolio Tracking** - Add/remove stocks, monitor holdings
- **Fast & Cached** - 5-second TTL caching + parallel loading
- **Responsive** - Desktop, tablet, mobile ready

---

## 🔑 Login

```
Email: test@arthsetu.com
Password: test123
```

---

## 📊 Top 13 Stocks

TCS • INFY • WIPRO • RELIANCE • ITC • BAJAJFINSV • HDFCBANK • AXISBANK • MARUTI • LT • NESTLEIND • PHARMACIE • GICRE

---

## 🛠 Tech Stack

**Backend**: Flask, Python 3.8+  
**Frontend**: HTML5, CSS3, JavaScript, Chart.js  
**Data**: Alpha Vantage, Yahoo Finance, NSE  
**Database**: SQLite  
**Deployment**: Docker ready

---

## 📡 API Endpoints

```
GET  /                            Dashboard
GET  /api/market/recommendations  13 recommendations
GET  /api/market/sentiment        6 indicators
GET  /api/market/performance      5 indices
GET  /api/analysis/complete/<sym> Stock analysis
```

---

## 📚 Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Full installation guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - What was built
- [PLATFORM_READY.md](PLATFORM_READY.md) - Production checklist

---

**Version**: 2.0 | Open Source | MIT License
