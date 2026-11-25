"""Weekly: checks SEC EDGAR for share offerings and share-count growth, writes sec.json.
pip install requests ; python update_sec.py
SEC requires a contact in the User-Agent: edit UA below before running.
"""
import json, datetime, requests

UA = {"User-Agent": "biotech-tracker your-email@example.com"}
TICKERS = ["MLYS","COGT","CORT","ANAB","ALT","CNTB","NGEN","VKTX","KURA","SVRA"]
FORMS = {"424B5","424B4","424B3","S-3","S-3ASR","S-1"}   # offerings and shelf registrations
today = datetime.date.today()
get = lambda u: requests.get(u, headers=UA, timeout=30).json()
ciks = {v["ticker"]: str(v["cik_str"]).zfill(10) for v in get("https://www.sec.gov/files/company_tickers.json").values()}

out = {"asof": today.strftime("%b %d, %Y"), "co": {}}
for t in TICKERS:
    try:
        c = ciks[t]
        rec = get(f"https://data.sec.gov/submissions/CIK{c}.json")["filings"]["recent"]
        offers = []
        for f, d, a, doc in zip(rec["form"], rec["filingDate"], rec["accessionNumber"], rec["primaryDocument"]):
            age = (today - datetime.date.fromisoformat(d)).days
            if f in FORMS and age <= 180:
                offers.append({"form": f, "date": d, "recent": age <= 14,
                               "url": f"https://www.sec.gov/Archives/edgar/data/{int(c)}/{a.replace('-','')}/{doc}"})
        facts = get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{c}/dei/EntityCommonStockSharesOutstanding.json")
        pts = {p["end"]: p["val"] for p in facts["units"]["shares"]}
        ends = sorted(pts)
        latest = pts[ends[-1]]
        yr_ago = [e for e in ends if (datetime.date.fromisoformat(ends[-1]) - datetime.date.fromisoformat(e)).days >= 300]
        growth = latest / pts[yr_ago[-1]] - 1 if yr_ago else None
        out["co"][t] = {"shares": latest, "shares_date": ends[-1], "growth_1y": growth,
                        "suggested": None if growth is None else max(0, min(30, round(growth * 100))),
                        "offerings": offers}
    except Exception as e:
        print(t, "failed:", e)
json.dump(out, open("sec.json", "w"), indent=1)
