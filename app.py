import streamlit as st
from auth import login_ui, signup_ui, logout
from theme import apply_theme

# ---------------------------------------------------
# PAGE CONFIG (ONLY ONCE, ONLY HERE)
# ---------------------------------------------------
st.set_page_config(
    page_title="CoinFetti",
    page_icon="📈",
    layout="wide"
)

apply_theme()

# ---------------------------------------------------
# AUTH GATE
# ---------------------------------------------------
if "user" not in st.session_state:

    st.title("📈 CoinFetti Finance App")

    st.markdown("""
    Welcome to a **CoinFetti finance analytics platform**.

    Please **login or create an account** to continue.
    """)

    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Signup"])

    with tab1:
        login_ui()

    with tab2:
        signup_ui()

    #  STOP HERE — pages are NOT accessible
    st.stop()

# ---------------------------------------------------
# LOGGED-IN LAYOUT
# ---------------------------------------------------

# Sidebar header
st.sidebar.markdown("##  CoinFetti Finance App")
st.sidebar.success(f" Logged in as **{st.session_state.user}**")

# Logout
if st.sidebar.button("🚪 Logout"):
    logout()

# ---------------------------------------------------
# SIDEBAR NAVIGATION (DISPLAY ONLY)
# ---------------------------------------------------
st.sidebar.markdown("---")

st.sidebar.markdown("""
⬅ Use the **Streamlit page selector above** to navigate.
""")

# ---------------------------------------------------
# MAIN LANDING PAGE (HOME)
# ---------------------------------------------------
st.title(" Welcome to CoinFetti Finance App")

st.markdown("""
This platform allows you to:

###  Explore Stocks
Detailed charts, fundamentals & price history.

###  Compare Stocks
Side-by-side data, PE ratio, EPS and comparative charts.

###  Portfolio Simulator
Live holdings, allocation chart and a saved watchlist.

###  Mutual Funds
Fund comparison, NAV trends and 1Y / 6M / 3M returns.

###  Analytics & News
Moving averages, RSI, risk metrics and market news.

---

 Use the **left sidebar page selector** to explore each module.
""")

# ---------------------------------------------------
# FOOTER
# ---------------------------------------------------
st.markdown("---")

