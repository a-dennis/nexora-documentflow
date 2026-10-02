"""Privacy-light visitor stats stored in the existing Supabase `usage` table.
Stores only: path, source (utm/ref host or direct), and a daily-rotating anonymous hash.
No IP or user agent is saved. Shown on /admin."""
import hashlib
import html as _h
import os
import urllib.parse
from collections import Counter
from datetime import datetime, timedelta, timezone

_DONE = {"v": False}
_SALT = os.urandom(8).hex()
BOT = ("bot", "crawl", "spider", "slurp", "preview", "facebookexternalhit", "whatsapp", "telegram", "render/", "uptime",
       "monitor", "curl", "wget", "python-requests", "httpx", "headless", "lighthouse", "pingdom", "go-http", "scrapy")
SKIP = ("/api", "/auth", "/buy", "/pay-thanks", "/admin", "/offline", "/icons", "/sw.js", "/og-image", "/manifest", "/health")
IST = timedelta(hours=5, minutes=30)


def install(g):
    if _DONE["v"]:
        return
    _DONE["v"] = True
    app = g["app"]
    from fastapi import Request

    @app.middleware("http")
    async def visit_mw(request: Request, call_next):
        resp = await call_next(request)
        try:
            p = request.url.path
            if (request.method == "GET" and resp.status_code == 200 and not p.startswith(SKIP)
                    and "text/html" in resp.headers.get("content-type", "")):
                ua = request.headers.get("user-agent", "")
                if ua and not any(b in ua.lower() for b in BOT):
                    ip = (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
                          or (request.client.host if request.client else ""))
                    day = (datetime.now(timezone.utc) + IST).strftime("%Y-%m-%d")
                    v = hashlib.sha256((ip + "|" + ua + "|" + day + "|" + _SALT).encode()).hexdigest()[:12]
                    q = request.query_params
                    src = (q.get("utm_source") or q.get("s") or "").strip().lower()[:30]
                    if not src:
                        ref = request.headers.get("referer", "")
                        host = urllib.parse.urlparse(ref).netloc.lower() if ref else ""
                        if host.startswith("www."):
                            host = host[4:]
                        src = "" if host.endswith("onrender.com") else host[:40]
                    g["db_insert_async"]("usage", {"event": "visit", "meta": {"p": p[:80], "src": src or "direct", "v": v}})
        except Exception as e:
            print("STATS_ERR", repr(e))
        return resp

    def fetch(days=8):
        since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        rows = []
        for k in range(20):
            part = g["_db_request"]("GET", "usage?event=eq.visit&created_at=gte." + since
                                    + "&select=created_at,meta&order=created_at.desc&limit=1000&offset=" + str(k * 1000))
            if not isinstance(part, list):
                break
            rows += part
            if len(part) < 1000:
                break
        return rows

    def e(x):
        return _h.escape(str(x))

    def table(head, rows):
        th = "".join(f"<th>{e(h)}</th>" for h in head)
        tr = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows) or f'<tr><td colspan="{len(head)}">No data yet</td></tr>'
        return f"<table><tr>{th}</tr>{tr}</table>"

    def visitor_html():
        rows = fetch()
        now = datetime.now(timezone.utc) + IST
        today = now.strftime("%Y-%m-%d")
        yday = (now - timedelta(days=1)).strftime("%Y-%m-%d")
        days7 = [(now - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]
        per = {d: [0, set()] for d in days7}
        pages, srcs, vis7 = Counter(), Counter(), set()
        for r in rows:
            try:
                d = (datetime.strptime(str(r["created_at"])[:19], "%Y-%m-%dT%H:%M:%S") + IST).strftime("%Y-%m-%d")
            except Exception:
                continue
            m = r.get("meta") or {}
            if d in per:
                per[d][0] += 1
                per[d][1].add(m.get("v"))
                pages[m.get("p", "?")] += 1
                srcs[m.get("src", "direct")] += 1
                vis7.add((d, m.get("v")))
        t = lambda d: (per[d][0], len(per[d][1]))
        summ = table(["", "Page views", "Visitors (approx)"],
                     [("Today", *t(today)), ("Yesterday", *t(yday)),
                      ("Last 7 days", sum(v[0] for v in per.values()), len(vis7))])
        daily = table(["Day (IST)", "Page views", "Visitors"], [(d, per[d][0], len(per[d][1])) for d in days7])
        return ("<h2>Visitors</h2>" + summ + "<h3>Per day</h3>" + daily
                + "<h3>Top pages (7 days)</h3>" + table(["Page", "Views"], pages.most_common(15))
                + "<h3>Sources (7 days)</h3>" + table(["Source", "Views"], srcs.most_common(10))
                + "<p style='font-size:13px;color:#52637a'>Counts page views of normal browsers; bots and link-preview fetchers are skipped. "
                  "Visitors are approximate (an anonymous hash that changes every day, so the 7-day figure counts a returning person once per day). "
                  "No IP or device details are stored. Many apps, including WhatsApp, send no referrer, so those show as direct. "
                  "To track a link, add ?s=name, for example <code>/?s=wa-status</code>, and it shows up under Sources. Counting started when this was deployed.</p>")

    g["_visitor_html"] = visitor_html
