"""Stock fundamentals with a fallback.

Yahoo often blocks the detailed `.info` request from cloud servers (it returns
nothing), while price history still works. When that happens we fill in what
we can from `fast_info`, which is built from the price data.
"""
import yfinance as yf

FALLBACKS = {
    "currentPrice": "last_price",
    "marketCap": "market_cap",
    "fiftyTwoWeekHigh": "year_high",
    "fiftyTwoWeekLow": "year_low",
}


def get_info(symbol):
    ticker = yf.Ticker(symbol)
    try:
        info = dict(ticker.info or {})
    except Exception:
        info = {}

    missing = [k for k in FALLBACKS if info.get(k) is None]
    if missing:
        try:
            fast = ticker.fast_info
        except Exception:
            fast = None
        if fast is not None:
            for key in missing:
                try:
                    value = fast[FALLBACKS[key]]
                except Exception:
                    value = None
                if value is not None:
                    info[key] = value

    if info.get("trailingPE") is None and info.get("trailingEps") and info.get("currentPrice"):
        info["trailingPE"] = info["currentPrice"] / info["trailingEps"]
    return info
