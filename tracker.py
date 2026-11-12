import re, json, csv, os, urllib.request, datetime as dt
JST = dt.timezone(dt.timedelta(hours=9))
LOG = 'balance_log.csv'
def get(u):
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    return urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'ignore')
h = get('https://andonlabs.com/radio')
m = re.search(r'balance:([\d.-]+),twitterUsername:"andon_grok_roll"', h)
if not m:
    raise SystemExit('balance not found')
bal = round(float(m.group(1)), 2)
try:
    d = json.loads(get('https://api.live365.com/station/a15419'))
    c = d.get('current-track') or {}
    now = f"{c.get('artist','')} - {c.get('title','')}"
except Exception:
    now = ''
rows = list(csv.reader(open(LOG))) if os.path.exists(LOG) else []
last = float(rows[-1][1]) if len(rows) > 1 else None
if last is None or bal != last:
    ch = '' if last is None else f'{bal - last:+.2f}'
    kind = 'start' if last is None else ('in (donation)' if bal > last else 'out (purchase?)')
    new = not os.path.exists(LOG)
    with open(LOG, 'a', newline='') as f:
        w = csv.writer(f)
        if new: w.writerow(['time_jst', 'balance', 'change', 'kind', 'now_playing'])
        w.writerow([dt.datetime.now(JST).strftime('%Y-%m-%d %H:%M'), f'{bal:.2f}', ch, kind, now])
    print('changed', bal, ch)
else:
    print('no change', bal)
