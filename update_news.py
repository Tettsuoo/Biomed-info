"""Weekly: Claude searches the web for each company and writes news.json,
including flags for anything that means the tracker's assumptions need editing.
pip install anthropic ; ANTHROPIC_API_KEY=... python update_news.py
Keep CURRENT in sync with the event dates (dt) in index.html.
"""
import json, re, datetime, anthropic

NAMES = {"MLYS":"Mineralys Therapeutics","COGT":"Cogent Biosciences","CORT":"Corcept Therapeutics",
         "ANAB":"AnaptysBio","ALT":"Altimmune","CNTB":"Connect Biopharma","NGEN":"NervGen Pharma",
         "VKTX":"Viking Therapeutics","KURA":"Kura Oncology","SVRA":"Savara"}
CURRENT = {"MLYS":("FDA decision","2026-12-22"),"COGT":("FDA decision","2026-12-30"),
           "CORT":("FDA decision","2026-12-17"),"ANAB":("FDA decision","2026-12-12"),
           "ALT":("FDA meeting","2026-12-15"),"CNTB":("FDA meeting","2026-12-15"),
           "NGEN":("Phase 3 topline","2028-03-31"),"VKTX":("Phase 3 results","2027-09-30"),
           "KURA":("Phase 3 topline","2028-06-30"),"SVRA":("FDA decision",None)}
PROMPT = """Search the web for news from the last 14 days about {n} ({t}). Cover trial updates, FDA
communications and dates, financing, cash runway, partnerships, analyst moves and competitor news that
matter to investors. Write in your own words, never copy article text.
My tracker currently assumes: {e} on {d}.
Reply with JSON only:
{{"summary":"3-4 sentences",
"items":[{{"title":"","date":"YYYY-MM-DD","why":"1-2 sentences on why it matters","url":""}}],
"event_date":"YYYY-MM-DD of the next {e} per the latest news, or null if unknown or not announced",
"flags":[{{"item":"what to change in the tracker","why":"the news behind it"}}]}}
Use at most 5 items and only real URLs you found. Add a flag only if the tracker needs editing: the
event date moved, the decision or result already happened, a major financing or trial failure changes
the odds or upside/downside assumptions, or the price left the $1-100 range. Otherwise flags is []."""
client = anthropic.Anthropic()
out = {"asof": datetime.date.today().strftime("%b %d, %Y"), "co": {}}
for t, n in NAMES.items():
    try:
        e, d = CURRENT[t]
        r = client.messages.create(model="claude-sonnet-4-6", max_tokens=2000,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 5}],
            messages=[{"role": "user", "content": PROMPT.format(n=n, t=t, e=e, d=d or "an unknown date")}])
        txt = "".join(b.text for b in r.content if b.type == "text")
        out["co"][t] = json.loads(re.search(r"\{.*\}", txt, re.S).group(0))
    except Exception as ex:
        print(t, "failed:", ex)
json.dump(out, open("news.json", "w"), indent=1)
