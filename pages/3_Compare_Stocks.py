import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
from theme import apply_theme

apply_theme()
st.title(" Compare Stocks")

# --------------------------
# CONFIG
# --------------------------
USD_INR = 90.0
CACHE_VERSION = "v2_inr_fix"   # 🔥 CRITICAL: busts old cache

# --------------------------
# Popular Tickers
# --------------------------
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

# --------------------------
# Stock Selectors
# --------------------------
colA, colB = st.columns(2)

ticker_name_1 = colA.selectbox("Select Stock 1", list(all_tickers.keys()))
ticker_name_2 = colB.selectbox("Select Stock 2", list(all_tickers.keys()))

symbol1 = all_tickers[ticker_name_1]
symbol2 = all_tickers[ticker_name_2]

# --------------------------
# FUNDAMENTALS (CACHE SAFE)
# --------------------------
@st.cache_data(ttl=3600)
def get_fundamentals(sym, cache_key):
    info = yf.Ticker(sym).info or {}
    is_india = sym.endswith(".NS")

    def convert(val):
        if val is None:
            return None
        return val if is_india else val * USD_INR

    return {
        "Current Price": convert(info.get("currentPrice")),
        "Market Cap": convert(info.get("marketCap")),
        "PE Ratio": info.get("trailingPE"),     # unitless
        "EPS": convert(info.get("trailingEps")),
        "52W High": convert(info.get("fiftyTwoWeekHigh")),
        "52W Low": convert(info.get("fiftyTwoWeekLow")),
    }

# --------------------------
# HISTORY (CACHE SAFE)
# --------------------------
@st.cache_data(ttl=1800)
def get_history(sym, cache_key):
    df = yf.Ticker(sym).history(period="6mo")
    if df is None or df.empty:
        return None

    series = df["Close"]
    if not sym.endswith(".NS"):
        series = series * USD_INR

    return series

# --------------------------
# LOAD DATA
# --------------------------
f1 = get_fundamentals(symbol1, CACHE_VERSION)
f2 = get_fundamentals(symbol2, CACHE_VERSION)

# --------------------------
# FUNDAMENTALS TABLE
# --------------------------
st.subheader(" Fundamentals Comparison")

rows = [
    "Current Price",
    "Market Cap",
    "PE Ratio",
    "EPS",
    "52W High",
    "52W Low",
]

df_compare = pd.DataFrame({
    "Metric": rows,
    ticker_name_1: [f1.get(r) for r in rows],
    ticker_name_2: [f2.get(r) for r in rows],
})

currency_rows = [
    "Current Price",
    "Market Cap",
    "EPS",
    "52W High",
    "52W Low",
]

for col in [ticker_name_1, ticker_name_2]:
    def format_cell(row):
        val = row[col]
        if (
            row["Metric"] in currency_rows
            and isinstance(val, (int, float))
        ):
            return f"₹{val:,.2f}"
        return val

    df_compare[col] = df_compare.apply(format_cell, axis=1)


st.dataframe(df_compare, use_container_width=True)

# --------------------------
# PRICE COMPARISON CHART
# --------------------------
st.subheader(" Price Comparison (6 Months)")

h1 = get_history(symbol1, CACHE_VERSION)
h2 = get_history(symbol2, CACHE_VERSION)

if h1 is None or h2 is None:
    st.warning("⚠️ Yahoo Finance rate-limited data. Try again later.")
else:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(h1.index, h1.values, label=ticker_name_1)
    ax.plot(h2.index, h2.values, label=ticker_name_2)
    ax.set_ylabel("Price (₹)")
    ax.set_title("Stock Price Comparison (INR)")
    ax.legend()
    st.pyplot(fig)

