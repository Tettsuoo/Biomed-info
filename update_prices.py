"""Hourly: writes prices.json (latest price, market cap, ~1 month of hourly closes).
pip install yfinance ; python update_prices.py
Quotes come from Yahoo via yfinance: unofficial and usually delayed ~15 minutes.
"""
import json, datetime, yfinance as yf

TICKERS = ["MLYS","COGT","CORT","ANAB","ALT","CNTB","NGEN","VKTX","KURA","SVRA"]
out = {"asof": datetime.datetime.utcnow().strftime("%b %d, %Y %H:%M UTC"), "t": {}}
for t in TICKERS:
    try:
        tk = yf.Ticker(t)
        h = tk.history(period="1mo", interval="1h")["Close"].dropna()
        out["t"][t] = {"px": round(float(h.iloc[-1]), 2),
                       "mcap": tk.fast_info.get("market_cap"),
                       "hist": [[i.isoformat(), round(float(v), 2)] for i, v in h.items()]}
    except Exception as e:
        print(t, "failed:", e)
json.dump(out, open("prices.json", "w"))
