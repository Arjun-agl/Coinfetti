import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import requests

# THEME (must be first Streamlit command)
from theme import apply_theme
apply_theme()

# ------------------------------
#  TICKERS
# ------------------------------
india_tickers = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
    "LT": "LT.NS",
    "Bharti Airtel": "BHARTIARTL.NS",
    "Maruti Suzuki": "MARUTI.NS",
    "Asian Paints": "ASIANPAINT.NS",
    "HUL": "HINDUNILVR.NS",
}

global_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
}

all_tickers = {**india_tickers, **global_tickers}

# Sidebar
st.sidebar.title(" Analytics & News")
selected_name = st.sidebar.selectbox("Choose a stock", list(all_tickers.keys()))
symbol = all_tickers[selected_name]
period = st.sidebar.selectbox("Period", ["6mo", "1y", "2y"], index=1)

# ------------------------------
#  DATA FETCHERS
# ------------------------------

@st.cache_data(ttl=3600)
def get_price_data(sym, per):
    try:
        df = yf.Ticker(sym).history(period=per, interval="1d")
        if df is None or df.empty:
            return None
        df = df.dropna()
        return df
    except:
        return None

@st.cache_data(ttl=3600)
def get_info(sym):
    try:
        return yf.Ticker(sym).info
    except:
        return None

# NEW — Yahoo Finance Search API (works reliably)
@st.cache_data(ttl=900)
def fetch_yahoo_news(query, count=10):
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {"q": query, "newsCount": count, "quotesCount": 0}

    try:
        r = requests.get(url, params=params, headers={"User-Agent": "Mozilla/5.0"})
        data = r.json()
        news_items = data.get("news", [])

        results = []
        for item in news_items:
            results.append({
                "title": item.get("title"),
                "publisher": item.get("publisher"),
                "link": item.get("link"),
                "published": item.get("providerPublishTime"),
            })
        return results
    except:
        return []


# ------------------------------
#  PAGE TITLE
# ------------------------------
st.title(f" Deep Analytics &  News — {selected_name} ({symbol})")

df = get_price_data(symbol, period)
info = get_info(symbol)

if df is None:
    st.error("⚠️ Yahoo Finance blocked OHLC data temporarily. Try again later.")
    st.stop()

# ------------------------------
#  RETURNS & RISK
# ------------------------------
st.subheader("Performance & Risk Dashboard")

df["Returns"] = df["Close"].pct_change()
daily_mean = df["Returns"].mean()
daily_std = df["Returns"].std()

trading_days = 252
annual_return = (1 + daily_mean) ** trading_days - 1 if not np.isnan(daily_mean) else None
annual_vol = daily_std * np.sqrt(trading_days) if not np.isnan(daily_std) else None

c1, c2, c3 = st.columns(3)
c1.metric("Annual Return", f"{annual_return*100:,.2f}%" if annual_return else "—")
c2.metric("Annual Volatility", f"{annual_vol*100:,.2f}%" if annual_vol else "—")
c3.metric("Market Cap", f"{info.get('marketCap'):,}" if info and info.get("marketCap") else "—")

# ------------------------------
#  TECHNICAL ANALYTICS
# ------------------------------
st.subheader(" Technical Indicators")

df["MA20"] = df["Close"].rolling(20).mean()
df["MA50"] = df["Close"].rolling(50).mean()

def compute_rsi(series, window=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.rolling(window).mean()
    avg_loss = loss.rolling(window).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

df["RSI"] = compute_rsi(df["Close"])

# Chart 1 — Price + MA
fig1, ax1 = plt.subplots(figsize=(10, 4))
ax1.plot(df.index, df["Close"], label="Close")
ax1.plot(df.index, df["MA20"], label="MA20")
ax1.plot(df.index, df["MA50"], label="MA50")
ax1.legend()
ax1.set_title("Price & Moving Averages")
st.pyplot(fig1)

# Chart 2 — RSI
fig2, ax2 = plt.subplots(figsize=(10, 3))
ax2.plot(df.index, df["RSI"])
ax2.axhline(70, color='red', linestyle='--')
ax2.axhline(30, color='green', linestyle='--')
ax2.set_title("RSI Indicator")
st.pyplot(fig2)

# ------------------------------
#  NEWS SECTION
# ------------------------------
st.subheader(" Latest News (Past Week)")

news = fetch_yahoo_news(selected_name)

if not news:
    st.info("⚠️ No news found for this stock (Yahoo sometimes restricts news).")
else:
    for item in news:
        title = item["title"]
        publisher = item["publisher"]
        link = item["link"]
        ts = item["published"]

        if ts:
            date = datetime.fromtimestamp(ts).strftime("%d %b %Y")
        else:
            date = "Unknown"

        st.markdown(f"### [{title}]({link})")
        st.caption(f"{publisher} · {date}")
        st.markdown("---")
