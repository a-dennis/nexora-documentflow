"""Payment fixes: loaded at the end of app.py. Replaces the payment routes."""

PATHS = {"/api/pay/order", "/api/pay/verify", "/api/premium/{product}", "/api/purchases"}

SRC = r'''def _rzp_get(path: str):
    """GET from the Razorpay REST API. Returns (status, json)."""
    import urllib.request
    import urllib.error
    import base64
    req = urllib.request.Request("https://api.razorpay.com/v1/" + path, method="GET")
    cred = base64.b64encode(
        (RAZORPAY_KEY_ID + ":" + RAZORPAY_KEY_SECRET).encode()).decode()
    req.add_header("Authorization", "Basic " + cred)
    try:
        with urllib.request.urlopen(req, timeout=12) as r:
            return r.status, json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode() or "{}")
        except Exception:
            return e.code, {}
    except Exception:
        traceback.print_exc()
        return 0, {}


_PROFILE_OK: set = set()


def _ensure_profile(user: dict) -> bool:
    """payments/purchases have a foreign key to profiles(id); make sure the
    signed-in user has a profile row (id = auth user id). Idempotent."""
    import urllib.request
    uid = user.get("id", "")
    if not uid:
        return False
    if uid in _PROFILE_OK:
        return True
    if not db_ready():
        return False
    row = {"id": uid, "email": user.get("email", "")}
    req = urllib.request.Request(SUPABASE_URL + "/rest/v1/profiles?on_conflict=id",
                                 data=json.dumps(row).encode(), method="POST")
    req.add_header("apikey", SUPABASE_SERVICE_KEY)
    req.add_header("Authorization", "Bearer " + SUPABASE_SERVICE_KEY)
    req.add_header("Content-Type", "application/json")
    req.add_header("Prefer", "resolution=ignore-duplicates,return=minimal")
    try:
        with urllib.request.urlopen(req, timeout=8):
            pass
    except Exception:
        traceback.print_exc()
        # A profile with the same email but another id would block the insert.
        return False
    ok = _db_request("GET", "profiles?id=eq." + uid + "&select=id&limit=1")
    if isinstance(ok, list) and ok:
        _PROFILE_OK.add(uid)
        return True
    return False


def _grant_payment(user: dict, order_id: str, payment_id: str, product: str,
                   amount: int) -> bool:
    """Record a verified payment and credit the purchase. Safe to call twice."""
    if not _ensure_profile(user):
        return False
    row = _payment_row(order_id)
    if row and row.get("status") == "verified":
        return True
    if row:
        _db_request("PATCH", "payments?razorpay_order_id=eq." + order_id,
                    {"status": "verified", "razorpay_payment_id": payment_id,
                     "user_id": user["id"]})
    else:
        if not db_insert("payments", {
                "user_id": user["id"], "razorpay_order_id": order_id,
                "razorpay_payment_id": payment_id, "amount_paise": amount,
                "currency": "INR", "status": "verified", "product": product}):
            return False
    db_insert("purchases", {"user_id": user["id"], "product": product,
                            "unlocked": True})
    db_usage("purchase", {"product": product})
    return True


_RECOVER_AT: dict = {}


def _recover_payments(user: dict) -> int:
    """Find paid Razorpay orders for this signed-in user that were never
    credited (for example the database write failed) and credit them.
    Matches on the email stored on the order. Returns how many were fixed."""
    if not (RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET and db_ready()):
        return 0
    email = (user.get("email") or "").strip().lower()
    uid = user.get("id", "")
    if not email or not uid:
        return 0
    now = time.time()
    if now - _RECOVER_AT.get(uid, 0) < 60:
        return 0
    _RECOVER_AT[uid] = now
    status, data = _rzp_get("orders?count=50")
    items = data.get("items") if isinstance(data, dict) else None
    if status != 200 or not isinstance(items, list):
        return 0
    fixed = 0
    for o in items:
        notes = o.get("notes") if isinstance(o.get("notes"), dict) else {}
        product = str(notes.get("product") or "")
        if product not in PAID_PRODUCTS:
            continue
        if str(notes.get("email") or "").strip().lower() != email:
            continue
        order_id = str(o.get("id") or "")
        if not order_id:
            continue
        prow = _payment_row(order_id)
        if prow and prow.get("status") == "verified":
            continue
        st, pays = _rzp_get("orders/" + order_id + "/payments")
        plist = pays.get("items") if isinstance(pays, dict) else None
        if st != 200 or not isinstance(plist, list):
            continue
        good = None
        for pay in plist:
            if pay.get("status") == "captured":
                good = pay
                break
            if pay.get("status") == "authorized":
                cs, cap = _rzp_call("payments/" + str(pay.get("id")) + "/capture",
                                    {"amount": pay.get("amount"),
                                     "currency": pay.get("currency", "INR")})
                if cs in (200, 201):
                    good = pay
                    break
        if not good:
            continue
        if _grant_payment(user, order_id, str(good.get("id") or ""), product,
                          int(o.get("amount") or 0)):
            fixed += 1
            print("RECOVERED payment", order_id, product)
    return fixed


def _verify_signature(order_id: str, payment_id: str, signature: str) -> bool:
    import hmac
    import hashlib
    expect = hmac.new(RAZORPAY_KEY_SECRET.encode(),
                      (order_id + "|" + payment_id).encode(),
                      hashlib.sha256).hexdigest()
    return hmac.compare_digest(expect, signature or "")


def _payment_row(order_id: str):
    rows = _db_request("GET", "payments?razorpay_order_id=eq." + order_id
                       + "&select=*")
    return rows[0] if isinstance(rows, list) and rows else None


@app.post("/api/pay/order")
async def api_pay_order(request: Request):
    if not payments_ready():
        return err_response(503, "Payments are being set up. Please check back soon.")
    if not db_ready():
        return err_response(503, "Payments are being set up. Please check back soon.")
    user = _current_user(request)
    if not user:
        return JSONResponse({"error": "Please sign in to continue.", "login": True},
                            status_code=401)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    product = str(payload.get("product") or "") if isinstance(payload, dict) else ""
    spec = PAID_PRODUCTS.get(product)
    if not spec:
        return err_response(404, "Unknown product.")
    if not _ensure_profile(user):
        return err_response(503, "Could not prepare your account for payment. "
                            "Please sign out, sign in again and retry. You have not been charged.")
    amount = spec["price_paise"]
    if spec.get("first_price_paise"):
        prior = _db_request("GET", "payments?user_id=eq." + user["id"]
                            + "&product=eq." + product
                            + "&status=eq.verified&select=id&limit=1")
        if not (isinstance(prior, list) and prior):
            amount = spec["first_price_paise"]
    receipt = "nx_" + uuid.uuid4().hex[:16]
    status, order = _rzp_call("orders", {
        "amount": amount,
        "currency": "INR",
        "receipt": receipt,
        "notes": {"product": product, "email": user.get("email", ""),
                  "user_id": user["id"]},
    })
    if status not in (200, 201) or not order.get("id"):
        return err_response(502, "Could not start the payment. Please try again.")
    if not db_insert("payments", {
            "user_id": user["id"],
            "razorpay_order_id": order["id"],
            "amount_paise": amount,
            "currency": "INR",
            "status": "created",
            "product": product}):
        return err_response(503, "Could not start the payment. You have not "
                            "been charged. Please try again.")
    return JSONResponse({
        "order_id": order["id"], "amount": amount,
        "currency": "INR", "key_id": RAZORPAY_KEY_ID,
        "product": product, "name": spec["name"],
        "email": user.get("email", "")})


@app.post("/api/pay/verify")
async def api_pay_verify(request: Request):
    if not payments_ready() or not db_ready():
        return err_response(503, "Payments are being set up. Please check back soon.")
    user = _current_user(request)
    if not user:
        return JSONResponse({"error": "Please sign in to continue.", "login": True},
                            status_code=401)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    order_id = str(payload.get("razorpay_order_id") or "")
    payment_id = str(payload.get("razorpay_payment_id") or "")
    signature = str(payload.get("razorpay_signature") or "")
    if not (order_id and payment_id and signature):
        return err_response(400, "Missing payment details.")
    row = _payment_row(order_id)
    if not row:
        # The order row was never saved. Rebuild it from Razorpay itself, but
        # only after the signature proves the payment, and only for this user.
        if _verify_signature(order_id, payment_id, signature):
            st, o = _rzp_get("orders/" + order_id)
            notes = (o.get("notes") if isinstance(o, dict) else None) or {}
            same = (str(notes.get("user_id") or "") == user["id"]
                    or str(notes.get("email") or "").strip().lower()
                    == (user.get("email") or "").strip().lower())
            product = str(notes.get("product") or "")
            if st == 200 and same and product in PAID_PRODUCTS and _grant_payment(
                    user, order_id, payment_id, product, int(o.get("amount") or 0)):
                return JSONResponse({"ok": True, "product": product})
        return err_response(404, "We could not match this payment yet. Do not "
                            "pay again - reload this page in a minute and it "
                            "will be unlocked automatically.")
    if row.get("user_id") != user["id"]:
        return err_response(404, "Unknown order.")
    if row.get("status") == "verified":
        return JSONResponse({"ok": True, "product": row.get("product"),
                             "already": True})
    if not _verify_signature(order_id, payment_id, signature):
        _db_request("PATCH", "payments?razorpay_order_id=eq." + order_id,
                    {"status": "failed"})
        return err_response(400, "Payment could not be verified. If any money was "
                            "deducted, Razorpay refunds it automatically.")
    if not _grant_payment(user, order_id, payment_id, row.get("product") or "",
                          int(row.get("amount_paise") or 0)):
        return err_response(503, "Payment received but unlocking is delayed. "
                            "Do not pay again - reload in a minute.")
    return JSONResponse({"ok": True, "product": row.get("product")})


@app.post("/api/premium/{product}")
async def api_premium(product: str, request: Request):
    spec = PAID_PRODUCTS.get(product)
    if not spec or not spec.get("prompt"):
        return err_response(404, "Unknown product.")
    if not db_ready():
        return err_response(503, "This feature is being set up. Please check back soon.")
    if not gemini_ready():
        return err_response(503, "The AI engine is being configured. Please try again shortly.")
    user = _current_user(request)
    if not user:
        return JSONResponse({"error": "Please sign in to continue.", "login": True},
                            status_code=401)
    credits = _db_request("GET", "purchases?user_id=eq." + user["id"]
                          + "&product=eq." + product
                          + "&unlocked=eq.true&select=id&limit=1")
    if not (isinstance(credits, list) and credits):
        return JSONResponse({"error": "This feature needs a one-time payment.",
                             "pay_required": True, "product": product,
                             "name": spec["name"],
                             "price_paise": spec["price_paise"]}, status_code=402)
    try:
        payload = await request.json()
    except Exception:
        payload = {}
    if not isinstance(payload, dict):
        payload = {}
    source_text = str(payload.get("source_text") or "")[:30000].strip()
    doc_id = str(payload.get("doc_id") or "").strip()
    if doc_id and not source_text:
        doc, err = doc_or_404(doc_id)
        if err:
            return err
        source_text = doc.get("text", "")[:30000]
    if len(source_text) < 40:
        return err_response(400, "Please paste " + spec["source_label"] + " first.")
    fields = {"target": str(payload.get("target") or "")[:500]}
    # Consume the credit before the AI run so a double-click cannot spend it twice.
    _db_request("PATCH", "purchases?id=eq." + str(credits[0]["id"]),
                {"unlocked": False})
    try:
        out = gemini_generate({"name": spec["name"], "text": source_text,
                               "raw": None},
                              spec["prompt"].format_map(_F(fields)))
    except Exception:
        traceback.print_exc()
        # AI failed - give the credit back.
        _db_request("PATCH", "purchases?id=eq." + str(credits[0]["id"]),
                    {"unlocked": True})
        return err_response(502, "The AI could not process this right now. "
                            "Your credit was not used - please try again.")
    db_history(doc_id or None, "premium:" + product,
               input_preview=source_text[:500], output_preview=out)
    db_usage("premium:" + product)
    return JSONResponse({"result": out})


@app.get("/api/purchases")
async def api_purchases(request: Request):
    user = _current_user(request)
    if not user:
        return JSONResponse({"authenticated": False, "purchases": []})
    try:
        _recover_payments(user)
    except Exception:
        traceback.print_exc()
    pro = _is_pro(request)
    rows = _db_request("GET", "purchases?user_id=eq." + user["id"]
                       + "&select=product,unlocked,created_at"
                       + "&order=created_at.desc&limit=50")
    return JSONResponse({"authenticated": True, "pro": pro,
                         "purchases": rows if isinstance(rows, list) else []})


'''


def install(g):
    app = g["app"]
    app.router.routes = [r for r in app.router.routes
                         if getattr(r, "path", None) not in PATHS]
    exec(compile(SRC, "payfix_src", "exec"), g)
