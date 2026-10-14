'''
import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from theme import apply_theme
#apply_theme()

#st.set_page_config(page_title="Mutual Funds", layout="wide")
apply_theme()
st.title("Mutual Fund Comparator")

# ---------------------------------------------------------
# 1️⃣ Fetch Mutual Fund List (via MFAPI.in)
# ---------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_all_funds():
    try:
        url = "https://api.mfapi.in/mf"
        data = requests.get(url).json()
        df = pd.DataFrame(data)
        return df
    except:
        return None

fund_list = fetch_all_funds()

if fund_list is None:
    st.error("Failed to load mutual fund list.")
    st.stop()

# Create dropdown-friendly mapping
fund_names = fund_list["schemeName"].tolist()
fund_codes = dict(zip(fund_list["schemeName"], fund_list["schemeCode"]))

# ---------------------------------------------------------
# 2️⃣ User selects two mutual funds to compare
# ---------------------------------------------------------
st.sidebar.header("Select Mutual Funds to Compare")

mf1_name = st.sidebar.selectbox("Mutual Fund A", fund_names)
mf2_name = st.sidebar.selectbox("Mutual Fund B", fund_names)

mf1_code = fund_codes[mf1_name]
mf2_code = fund_codes[mf2_name]

# ---------------------------------------------------------
# 3️⃣ Fetch NAV history for each fund
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_nav_history(code):
    try:
        url = f"https://api.mfapi.in/mf/{code}"
        data = requests.get(url).json()
        navs = data["data"]
        df = pd.DataFrame(navs)
        df["nav"] = df["nav"].astype(float)

        # FIX: handle DD-MM-YYYY format safely
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")

        df = df.sort_values("date")
        return df
    except:
        return None

df1 = fetch_nav_history(mf1_code)
df2 = fetch_nav_history(mf2_code)

if df1 is None or df2 is None:
    st.error("Could not load NAV history for selected funds.")
    st.stop()

# ---------------------------------------------------------
# 4️⃣ Calculate Returns (1-Year, 6-Month, 3-Month)
# ---------------------------------------------------------
def compute_return(df, days):
    try:
        recent = df.iloc[-1]["nav"]
        past_date = df["date"].max() - pd.Timedelta(days=days)
        past = df.loc[df["date"] >= past_date].iloc[0]["nav"]
        return round(((recent - past) / past) * 100, 2)
    except:
        return None

def summarize(df):
    return {
        "Latest NAV": df.iloc[-1]["nav"],
        "1Y Return %": compute_return(df, 365),
        "6M Return %": compute_return(df, 180),
        "3M Return %": compute_return(df, 90),
    }

summary1 = summarize(df1)
summary2 = summarize(df2)

# ---------------------------------------------------------
# 5️⃣ Display Comparison with Green/Red highlight
# ---------------------------------------------------------
st.subheader("Comparison Summary")

def color(val1, val2):
    if val1 is None or val2 is None:
        return ("gray", "gray")
    return ("green", "red") if val1 > val2 else ("red", "green")

labels = ["Latest NAV", "1Y Return %", "6M Return %", "3M Return %"]

for key in labels:
    c1, c2 = color(summary1[key], summary2[key])

    col1, col2, col3 = st.columns([3, 3, 3])
    col1.write(f"**{key}**")

    col2.markdown(f"<p style='color:{c1}; font-size:18px;'> {summary1[key]} </p>", unsafe_allow_html=True)
    col3.markdown(f"<p style='color:{c2}; font-size:18px;'> {summary2[key]} </p>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6️⃣ NAV Comparison Chart
# ---------------------------------------------------------
st.subheader(" NAV Trend Comparison")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df1["date"], df1["nav"], label=mf1_name)
ax.plot(df2["date"], df2["nav"], label=mf2_name)
ax.set_xlabel("Date")
ax.set_ylabel("NAV")
ax.legend()
st.pyplot(fig)
'''

import streamlit as st
import requests
import pandas as pd
import matplotlib.pyplot as plt
from theme import apply_theme

apply_theme()
st.title(" Mutual Fund Comparator")

# ---------------------------------------------------------
# 1️⃣ Fetch Mutual Fund List (MFAPI)
# ---------------------------------------------------------
@st.cache_data(ttl=86400)
def fetch_all_funds():
    try:
        url = "https://api.mfapi.in/mf"
        data = requests.get(url).json()
        return pd.DataFrame(data)
    except:
        return None

fund_list = fetch_all_funds()

if fund_list is None or fund_list.empty:
    st.error("Failed to load mutual fund list.")
    st.stop()

# ---------------------------------------------------------
# 2️⃣ FILTER TO POPULAR AMCs ONLY
# ---------------------------------------------------------
POPULAR_AMCS = [
    "HDFC",
    "ICICI",
    "SBI",
    "KOTAK",
    "MOTILAL OSWAL",
    "AXIS",
    "NIPPON",
    "ADITYA BIRLA",
]

mask = fund_list["schemeName"].str.upper().apply(
    lambda name: any(amc in name for amc in POPULAR_AMCS)
)

filtered_funds = fund_list[mask].copy()

# Remove IDCW / Dividend noise for cleaner UX
filtered_funds = filtered_funds[
    ~filtered_funds["schemeName"].str.contains("IDCW|DIVIDEND", case=False, na=False)
]

fund_names = filtered_funds["schemeName"].tolist()
fund_codes = dict(zip(filtered_funds["schemeName"], filtered_funds["schemeCode"]))

# ---------------------------------------------------------
# 3️⃣ USER SELECTION
# ---------------------------------------------------------
st.sidebar.header("Select Mutual Funds")

mf1_name = st.sidebar.selectbox("Mutual Fund A", fund_names)
mf2_name = st.sidebar.selectbox("Mutual Fund B", fund_names)

mf1_code = fund_codes[mf1_name]
mf2_code = fund_codes[mf2_name]

# ---------------------------------------------------------
# 4️⃣ FETCH NAV HISTORY
# ---------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_nav_history(code):
    try:
        url = f"https://api.mfapi.in/mf/{code}"
        data = requests.get(url).json()
        navs = data.get("data", [])
        df = pd.DataFrame(navs)

        if df.empty:
            return None

        df["nav"] = df["nav"].astype(float)
        df["date"] = pd.to_datetime(df["date"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["date"])
        df = df.sort_values("date")

        return df
    except:
        return None

df1 = fetch_nav_history(mf1_code)
df2 = fetch_nav_history(mf2_code)

if df1 is None or df2 is None:
    st.error("Could not load NAV history for selected funds.")
    st.stop()

# ---------------------------------------------------------
# 5️⃣ RETURN CALCULATIONS
# ---------------------------------------------------------
def compute_return(df, days):
    try:
        recent = df.iloc[-1]["nav"]
        past_date = df["date"].max() - pd.Timedelta(days=days)
        past = df.loc[df["date"] >= past_date].iloc[0]["nav"]
        return round(((recent - past) / past) * 100, 2)
    except:
        return None

def summarize(df):
    return {
        "Latest NAV": round(df.iloc[-1]["nav"], 2),
        "1Y Return %": compute_return(df, 365),
        "6M Return %": compute_return(df, 180),
        "3M Return %": compute_return(df, 90),
    }

summary1 = summarize(df1)
summary2 = summarize(df2)

# ---------------------------------------------------------
# 6️⃣ COMPARISON SUMMARY (GREEN / RED)
# ---------------------------------------------------------
st.subheader(" Comparison Summary")
# ---- Table Header Row ----
h1, h2, h3 = st.columns([3, 3, 3])
h1.markdown("### Metric")
h2.markdown(f"### {mf1_name}")
h3.markdown(f"### {mf2_name}")

st.markdown("---")
def color(v1, v2):
    if v1 is None or v2 is None:
        return ("gray", "gray")
    return ("green", "red") if v1 > v2 else ("red", "green")

metrics = ["Latest NAV", "1Y Return %", "6M Return %", "3M Return %"]

for m in metrics:
    c1, c2 = color(summary1[m], summary2[m])

    col1, col2, col3 = st.columns([3, 3, 3])
    col1.write(f"**{m}**")

    col2.markdown(
        f"<p style='color:{c1}; font-size:18px;'>{summary1[m]}</p>",
        unsafe_allow_html=True,
    )
    col3.markdown(
        f"<p style='color:{c2}; font-size:18px;'>{summary2[m]}</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------
# 7️⃣ NAV TREND COMPARISON
# ---------------------------------------------------------
st.subheader(" NAV Trend Comparison")

fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df1["date"], df1["nav"], label=mf1_name)
ax.plot(df2["date"], df2["nav"], label=mf2_name)
ax.set_xlabel("Date")
ax.set_ylabel("NAV")
ax.legend()
st.pyplot(fig)



