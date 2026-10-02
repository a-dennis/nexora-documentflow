"""Admin access: allowlisted emails (env ADMIN_EMAILS, comma separated) get Pro/unlimited
use and a read-only /admin page. Checked server-side from the signed session only."""
import html as _h
import os
import time
import urllib.parse

_DONE = {"v": False}
_ADM_IDS = {"t": 0.0, "ids": set()}


def _admin_emails():
    return {e.strip().lower() for e in os.environ.get("ADMIN_EMAILS", "").split(",") if e.strip()}


def install(g):
    if _DONE["v"]:
        return
    _DONE["v"] = True
    app = g["app"]
    orig_db = g["_db_request"]
    orig_cu = g["_current_user"]
    orig_pro = g["_is_pro"]
    from fastapi import Request
    from fastapi.responses import HTMLResponse, Response

    def is_admin_user(user):
        if not user:
            return False
        em = (user.get("email") or "").strip().lower()
        # email must be confirmed by Supabase (Google sign-in or confirmed email link)
        return bool(em and em in _admin_emails() and user.get("email_confirmed_at"))

    def is_admin(request):
        try:
            return is_admin_user(orig_cu(request))
        except Exception:
            return False

    def admin_ids():
        now = time.time()
        if now - _ADM_IDS["t"] < 60:
            return _ADM_IDS["ids"]
        ids = set()
        for em in _admin_emails():
            rows = orig_db("GET", "profiles?email=ilike." + urllib.parse.quote(em.replace("_", "\\_"), safe="@.") + "&select=id")
            if isinstance(rows, list):
                ids.update(r["id"] for r in rows if r.get("id"))
        _ADM_IDS.update(t=now, ids=ids)
        return ids

    def db_wrap(method, path, payload=None, return_rows=False):
        # Admin never spends or needs one-time credits.
        if method == "GET" and path.startswith("purchases?user_id=eq.") and "&unlocked=eq.true" in path:
            uid = path[len("purchases?user_id=eq."):].split("&", 1)[0]
            if _admin_emails() and uid in admin_ids():
                return [{"id": "admin-bypass"}]
        if method == "PATCH" and path == "purchases?id=eq.admin-bypass":
            return True
        return orig_db(method, path, payload, return_rows)

    def pro_wrap(request):
        return True if is_admin(request) else orig_pro(request)

    g["_db_request"] = db_wrap
    g["_is_pro"] = pro_wrap

    def e(x):
        return _h.escape(str(x if x is not None else ""))

    def table(head, rows):
        th = "".join(f"<th>{e(h)}</th>" for h in head)
        tr = "".join("<tr>" + "".join(f"<td>{e(c)}</td>" for c in r) + "</tr>" for r in rows) or f'<tr><td colspan="{len(head)}">None</td></tr>'
        return f"<table><tr>{th}</tr>{tr}</table>"

    @app.get("/admin")
    async def admin_page(request: Request):
        if not is_admin(request):
            return HTMLResponse("<!DOCTYPE html><title>Not found</title><h1>Page not found</h1>", status_code=404)
        user = orig_cu(request)
        emails = {}
        for r in (orig_db("GET", "profiles?select=id,email&limit=1000") or []):
            emails[r.get("id")] = r.get("email")
        pays = orig_db("GET", "payments?select=razorpay_order_id,razorpay_payment_id,amount_paise,status,product,user_id,created_at&order=created_at.desc&limit=40") or []
        purch = orig_db("GET", "purchases?select=product,unlocked,user_id,created_at&order=created_at.desc&limit=40") or []
        profs = orig_db("GET", "profiles?select=id&limit=1000") or []
        from datetime import datetime, timedelta, timezone
        since = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")
        pro = orig_db("GET", "payments?product=eq.pro_pass&status=eq.verified&created_at=gte." + since + "&select=user_id,created_at,razorpay_payment_id&order=created_at.desc&limit=100") or []
        pays = pays if isinstance(pays, list) else []
        purch = purch if isinstance(purch, list) else []
        pro = pro if isinstance(pro, list) else []
        stuck = [p for p in pays if p.get("status") not in ("verified",)]
        def pay_rows(src):
            return [(str(p.get("created_at", ""))[:16].replace("T", " "), emails.get(p.get("user_id"), p.get("user_id") or "-"), p.get("product"),
                     "Rs %s" % ((p.get("amount_paise") or 0) / 100), p.get("status"), (p.get("razorpay_payment_id") or "-")) for p in src]
        body = (f"<h1>Nexora admin</h1><p>Signed in as {e(user.get('email'))}. Read-only. You have Pro and unlimited use on this account.</p>"
                f"<h2>Summary</h2>" + table(["Profiles", "Recent payments shown", "Verified", "Not verified", "Pro (30 days)"],
                                            [(len(profs) if isinstance(profs, list) else "-", len(pays), len(pays) - len(stuck), len(stuck), len(pro))])
                + "<h2>Pro users (last 30 days)</h2>" + table(["Email", "Paid on", "Payment id"],
                    [(emails.get(p.get("user_id"), p.get("user_id")), str(p.get("created_at", ""))[:10], p.get("razorpay_payment_id") or "-") for p in pro])
                + "<h2>Recent payments</h2>" + table(["Time (UTC)", "User", "Product", "Amount", "Status", "Payment id"], pay_rows(pays))
                + "<h2>Recent purchases (credits)</h2>" + table(["Time (UTC)", "User", "Product", "Unlocked"],
                    [(str(p.get("created_at", ""))[:16].replace("T", " "), emails.get(p.get("user_id"), p.get("user_id")), p.get("product"), p.get("unlocked")) for p in purch])
                + "<h2>Recovery notes</h2><p>When a paid Razorpay order is missing in the database, the app credits it automatically the next time that buyer visits. Each recovery is logged in Render logs as <code>RECOVERED payment ...</code>. Payments above that are not verified are unpaid or abandoned orders.</p>"
                + '<p><a href="/">Back to Nexora</a></p>')
        doc = ("<!DOCTYPE html><html lang=\"en\"><head><!-- nx-seo --><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
               "<meta name=\"robots\" content=\"noindex,nofollow\"><title>Admin | Nexora</title><style>body{font-family:system-ui,Arial,sans-serif;margin:24px;max-width:1100px;color:#0f172a}"
               "table{border-collapse:collapse;width:100%;margin:8px 0 20px;font-size:14px}th,td{border:1px solid #e3e8f0;padding:6px 8px;text-align:left;word-break:break-all}th{background:#f6f8fb}</style></head><body>"
               + body + "</body></html>")
        return HTMLResponse(doc, headers={"Cache-Control": "no-store", "X-Robots-Tag": "noindex"})

    @app.get("/api/admin-status")
    async def admin_status(request: Request):
        return Response('{"admin":%s}' % ("true" if is_admin(request) else "false"), media_type="application/json", headers={"Cache-Control": "no-store"})

    rs = app.router.routes
    mine = [r for r in rs if getattr(r, "path", None) in ("/admin", "/api/admin-status")]
    for r in mine:
        rs.remove(r)
    rs[0:0] = mine
