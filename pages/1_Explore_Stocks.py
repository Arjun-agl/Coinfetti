import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import mplfinance as mpf
from datetime import datetime, timedelta
from theme import apply_theme
#apply_theme()

st.set_page_config(page_title="Explore Stocks", layout="wide")
apply_theme()
st.sidebar.title(" Explore Stocks")

# --- Popular Tickers ---
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

selected_name = st.sidebar.selectbox(
    "Choose a stock",
    list(all_tickers.keys()),
)

symbol = all_tickers[selected_name]

# --- Period options ---
period = st.sidebar.selectbox(
    "Select Period",
    ["1mo", "3mo", "6mo", "1y", "2y"],
    index=2
)

interval_map = {
    "1mo": "1d",
    "3mo": "1d",
    "6mo": "1d",
    "1y": "1d",
    "2y": "1d"
}

st.title(f" {selected_name} ({symbol})")

# ==============================
# SAFE YFINANCE WRAPPERS
# ==============================

@st.cache_data(ttl=3600, show_spinner="Fetching Data…")
def get_price_data(sym, per, interval):
    try:
        df = yf.Ticker(sym).history(period=per, interval=interval)
        if df is None or df.empty:
            return None
        df = df.dropna()
        df = df.astype(float)
        return df
    except Exception as e:
        return None


@st.cache_data(ttl=3600)
def get_fundamentals(sym):
    try:
        info = yf.Ticker(sym).info
        if not info:
            return None
        return {
            "Market Cap": info.get("marketCap"),
            "PE Ratio": info.get("trailingPE"),
            "EPS": info.get("trailingEps"),
            "52W High": info.get("fiftyTwoWeekHigh"),
            "52W Low": info.get("fiftyTwoWeekLow"),
        }
    except:
        return None


# ==============================
# LOAD DATA
# ==============================
df = get_price_data(symbol, period, interval_map[period])
funds = get_fundamentals(symbol)

# ==============================
# FUNDAMENTALS SECTION
# ==============================
st.subheader(" Fundamentals")

if funds:
    col1, col2, col3, col4, col5 = st.columns(5)

    col1.metric("Market Cap", f"{funds['Market Cap']:,}" if funds["Market Cap"] else "—")
    col2.metric("PE Ratio", funds["PE Ratio"] if funds["PE Ratio"] else "—")
    col3.metric("EPS", funds["EPS"] if funds["EPS"] else "—")
    col4.metric("52W High", funds["52W High"] if funds["52W High"] else "—")
    col5.metric("52W Low", funds["52W Low"] if funds["52W Low"] else "—")

else:
    st.warning("⚠️ Fundamentals not available right now. Yahoo is rate-limiting.")

# ==============================
# PRICE CHART SECTION
# ==============================
st.subheader(" Price Chart (Candlestick)")

if df is None or df.empty:
    st.error("⚠️ Chart data unavailable right now. Try again in 10–20 seconds.")
else:
    try:
        fig, ax = mpf.plot(
            df,
            type="candle",
            style="charles",
            ylabel="Price",
            title=f"{symbol} Candle Chart",
            returnfig=True,
            figsize=(12, 5)
        )
        st.pyplot(fig)
    except Exception as e:
        st.error(f"⚠️ Failed to load chart: {str(e)}")

# Show raw data toggle
with st.expander(" View Raw Data"):
    st.write(df)
