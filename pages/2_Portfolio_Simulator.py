import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from theme import apply_theme
from storage import load_portfolio, save_portfolio

apply_theme()

st.title("CoinFetti Portfolio Simulator")

# ===================================
# CONFIG
# ===================================
USD_INR = 90.0

india_tickers = {
    "Reliance Industries": "RELIANCE.NS",
    "TCS": "TCS.NS",
    "Infosys": "INFY.NS",
    "HDFC Bank": "HDFCBANK.NS",
    "ICICI Bank": "ICICIBANK.NS",
}

global_tickers = {
    "Apple": "AAPL",
    "Microsoft": "MSFT",
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "NVIDIA": "NVDA",
}

ALL_TICKERS = {**india_tickers, **global_tickers}

# ===================================
# LOAD USER PORTFOLIO (NO LOGIC CHANGE)
# ===================================
username = st.session_state.user
data = load_portfolio(username)

if "holdings" not in st.session_state:
    st.session_state.holdings = data.get("holdings", {})

if "watchlist" not in st.session_state:
    st.session_state.watchlist = set(data.get("watchlist", []))

# ===================================
# HELPERS
# ===================================

@st.cache_data(ttl=900)
def fetch_price(symbol):
    try:
        t = yf.Ticker(symbol)
        price = getattr(t, "fast_info", {}).get("last_price")
        if price is None:
            hist = t.history(period="1d")
            if not hist.empty:
                price = float(hist["Close"].iloc[-1])
        if price is None:
            return None
        return price if symbol.endswith(".NS") else price * USD_INR
    except:
        return None

@st.cache_data(ttl=600)
def fetch_history(symbol, period="1y"):
    try:
        df = yf.Ticker(symbol).history(period=period)
        if df.empty:
            return df
        df = df[["Close"]].rename(columns={"Close": "close"})
        if not symbol.endswith(".NS"):
            df["close"] *= USD_INR
        return df
    except:
        return pd.DataFrame()

@st.cache_data(ttl=600)
def fetch_info(symbol):
    try:
        return yf.Ticker(symbol).info
    except:
        return {}

# ============================================================
# SECTION 1 — MANAGE PORTFOLIO
# ============================================================

st.markdown("## Manage Your Portfolio")

with st.container():
    st.markdown("""
        <div style='padding:22px; border-radius:14px; background-color:#1e293b; margin-bottom:20px;'>
        <h4 style='margin-top:0;'>Add / Increase Stock</h4>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([3, 1.2, 1.3])

    selected_name = col1.selectbox("Select Stock", list(ALL_TICKERS.keys()))
    symbol = ALL_TICKERS[selected_name]
    qty_add = col2.number_input("Qty", min_value=1, value=1)

    with col3:
        st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
        add_btn = st.button("Add / Increase", use_container_width=True)

    if add_btn:
        if symbol in st.session_state.holdings:
            st.session_state.holdings[symbol]["qty"] += qty_add
        else:
            st.session_state.holdings[symbol] = {"name": selected_name, "qty": qty_add}

        save_portfolio(username, {
            "holdings": st.session_state.holdings,
            "watchlist": list(st.session_state.watchlist)
        })

        st.success(f"Updated {selected_name} ({symbol})")

    st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# REDUCE / REMOVE
# ============================================================

if st.session_state.holdings:
    st.markdown("### Edit Existing Holdings")

    with st.container():
        st.markdown("""
            <div style='padding:22px; border-radius:14px; background-color:#1e293b; margin-bottom:20px;'>
            <h4 style='margin-top:0;'>Modify Holding</h4>
        """, unsafe_allow_html=True)

        names = [
            f"{v['name']} ({k}) — {v['qty']}"
            for k, v in st.session_state.holdings.items()
        ]
        selected_row = st.selectbox("Select Holding", names)
        sym = selected_row.split("(")[1].split(")")[0]

        qty_col, reduce_btn_col, remove_btn_col = st.columns([1, 1, 1])

        with qty_col:
            reduce_qty = st.number_input("Reduce Qty", min_value=0, value=0, step=1)

        with reduce_btn_col:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            reduce_btn = st.button("Apply Reduce", use_container_width=True)

        with remove_btn_col:
            st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)
            remove_btn = st.button("Remove Stock", use_container_width=True)

        if reduce_btn:
            if reduce_qty <= 0:
                st.warning("Enter a quantity greater than 0.")
            elif reduce_qty >= st.session_state.holdings[sym]["qty"]:
                st.session_state.holdings.pop(sym)
            else:
                st.session_state.holdings[sym]["qty"] -= reduce_qty

            save_portfolio(username, {
                "holdings": st.session_state.holdings,
                "watchlist": list(st.session_state.watchlist)
            })

        if remove_btn:
            st.session_state.holdings.pop(sym)

            save_portfolio(username, {
                "holdings": st.session_state.holdings,
                "watchlist": list(st.session_state.watchlist)
            })

        st.markdown("</div>", unsafe_allow_html=True)

# ============================================================
# PORTFOLIO OVERVIEW
# ============================================================

st.markdown("## Portfolio Overview")

if not st.session_state.holdings:
    st.info("Portfolio empty. Add stocks above.")
    st.stop()

rows = []
for sym, d in st.session_state.holdings.items():
    qty = d["qty"]
    price = fetch_price(sym)
    value = price * qty if price else None

    rows.append({
        "Symbol": sym,
        "Name": d["name"],
        "Qty": qty,
        "Live Price (₹)": price,
        "Value (₹)": value,
    })

df = pd.DataFrame(rows)

display_df = df.copy()
display_df["Live Price (₹)"] = display_df["Live Price (₹)"].apply(lambda x: f"₹{x:,.2f}" if x else "—")
display_df["Value (₹)"] = display_df["Value (₹)"].apply(lambda x: f"₹{x:,.2f}" if x else "—")
display_df.index = range(1, len(display_df) + 1)
st.dataframe(display_df, use_container_width=True)

total_value = df["Value (₹)"].fillna(0).sum()

c1, c2 = st.columns(2)
c1.metric("Total Portfolio Value (₹)", f"{total_value:,.2f}")
c2.metric("Total Holdings", len(df))

# PIE CHART
st.markdown("### Portfolio Allocation")
valid_values = df["Value (₹)"].fillna(0)

if valid_values.sum() > 0:
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(valid_values, labels=df["Symbol"], autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)

# ============================================================
# WATCHLIST (SAVE ENABLED)
# ============================================================

st.sidebar.header(" Watchlist")

add_watch = st.sidebar.selectbox("Add to watchlist", list(ALL_TICKERS.keys()))
symw = ALL_TICKERS[add_watch]

if st.sidebar.button("Add"):
    st.session_state.watchlist.add(symw)

    save_portfolio(username, {
        "holdings": st.session_state.holdings,
        "watchlist": list(st.session_state.watchlist)
    })

for sym in list(st.session_state.watchlist):
    price = fetch_price(sym)
    st.sidebar.write(f"{sym}: ₹{price:,.2f}" if price else f"{sym}: —")

    if st.sidebar.button(f"Remove {sym}", key=f"rmw_{sym}"):
        st.session_state.watchlist.remove(sym)

        save_portfolio(username, {
            "holdings": st.session_state.holdings,
            "watchlist": list(st.session_state.watchlist)
        })

        st.rerun()
