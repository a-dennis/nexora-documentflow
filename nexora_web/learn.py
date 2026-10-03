"""Nexora learning sections (English, AI A-to-Z) - installed into the main app.
Own routes only: /english, /ai, /manifest.webmanifest, /sw.js, /icon-*.png,
/api/learn/*. Uses its own rate limit; never touches the document quota."""
import os, json, time, base64, urllib.request
from urllib.parse import quote
from fastapi import Request
from fastapi.responses import HTMLResponse, Response, JSONResponse, RedirectResponse

BASE = os.path.dirname(os.path.abspath(__file__))
ICON192 = base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAMAAAADACAIAAADdvvtQAAADQklEQVR42u3dsUodQRiG4R3xCtLkJiRNqiRlsLZKK4K1FxDIpYhVbkDIHSgiaHqDxamENBIhRC2EtfJUAd3dw47/P897ATJnnPN+35/ZNeXbx+sOGMt61/V2AeMPULEHYCAwEBgIDAQMPUAMhPGs2QKIMCjRYCAo0YASjVkNVBgIDAQlGsZ4MBBgjIcSDQYCAwEMBFMYRBhEGMBAWLGB3MaDgaADwRgPEQaIMDAQGAhKNPDcAfJMNBgIDAQGgjEeGGogt/EQYVCiwUBgIICB4ABBhIGBAAYCA72EjS9vPuy9jbLauz8P37cuGehV0VswA42nWHCdA5TmMjXaLyTHznucAyJMhCnRSjQD+UK3WaL9Q2K1A6REQ4lOY6BwH4SBALfx9Rq0MR7GeGO8BSvRQb/QOXZ+XZAs+bFzcbO4tw8DDVTSjPGTf0LpvehtjIcOVKlSlCy9xBRmMhJhEGHtRVgvwhgIDFTPYXaDgcBAOpAxPugMbzdEGETYWH9MRoQxEOY2UJ534yeXaLfxLZfo6R9k8+DdDOv8fXpz8vVXngPkmega5NlzBrJUBgr2te4ZCAxkjMeKDOQubG79FBEGEWaM1/cZyBjPQMZ4BsLQEp1pCit5fjFhlproBCnR0laEKdEM1NjXmoEycrz78+/iHwPpQAZsBqr0tebjEQdIB1qeHm9lDMbjHBBhK0ofb6Yq0Uo0A1V1mN1ot0T76xxKNCIayKvNyx9QOq82MxCU6EpjfKdEG+ON8QxUTR7G+KbHeHdhSjQYKHaEMRADgYF0IFNYyAh7v/9p5jWfbx/dXd2KMIgwVIrd6PvPQJhooDT/7XfAD5LgT5szEHSgwJNj+A5kjK+85uj7L8Igwp7iIKaBlGgwUAoiGkiJVqLbLtGeia5uTQZCY+LMaqA+5ppj7385+3xIAzDGo1YH8jY4lGgo0WAgMBDAQHCAIMLAQAADgYHAQGAg4D8HyGUqJuBxDogwKNFgIDR6gBgISjQYCAwEJRowxoOBoERDiQaeM5DbeDAQdCCYwiDCABEGBgIDgYEABoIxHiIMIgxgIKzaQG7joUSj2gHyTDQYCAwEBoIxHhhsIBEGEQYlGgwEBgIYCLPxCAdsxU5ky+MbAAAAAElFTkSuQmCC")
ICON512 = base64.b64decode("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")
MANIFEST = json.dumps({
    "name": "Nexora", "short_name": "Nexora",
    "description": "Documents and PDF tools, Markets, English and AI A-to-Z in one app.",
    "start_url": "/", "scope": "/", "display": "standalone",
    "background_color": "#ffffff", "theme_color": "#7c3aed",
    "icons": [
        {"src": "/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"}]})
SW = """self.addEventListener('install',e=>self.skipWaiting());
self.addEventListener('activate',e=>e.waitUntil(self.clients.claim()));
self.addEventListener('fetch',e=>{});"""
MODELS = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-2.0-flash"]
RATE = {}
TTS_CACHE = {}
KIDS = ("You are a friendly, gentle teacher for children aged 5 to 12 in India (first language Kannada or Hindi). "
 "Use very short, simple, happy sentences, at most 60 words. Only answer questions about learning: English words, letters, numbers, colors, animals, fruits, simple science, nature and good habits. "
 "If asked about anything else (violence, adult topics, dating, money, politics, religion debates, social media, strangers, games with chat, medicine, or anything scary), say kindly that you can only help with learning and suggest asking a parent or teacher. "
 "Never ask for or repeat the child's name, school, address, phone number or photos. If the child shares such details, tell them not to share it and ask a parent. "
 "Never tell the child to meet anyone or go anywhere. Add one very short explanation in the learner language named below, and do not use any other language. Never use scary words.")
import re as _re
_PII = _re.compile(r"(\d[\d\s-]{8,}\d|@[a-z0-9_.]+|https?://|\botp\b|password|aadhaar|aadhar|\bpin\b)", _re.I)
_BAD = _re.compile(r"\b(sex|porn|nude|kill|suicide|rape|drug|ganja|beer|whisky|alcohol|cigarette|gun|bomb|girlfriend|boyfriend|kiss|gamble|bet)\b", _re.I)


def _guard(track, text):
    if _PII.search(text):
        return "Please do not share phone numbers, passwords, OTP or personal details. Ask a parent if you are unsure."
    if track == "kids" and _BAD.search(text):
        return "I can only help with learning, like English words, numbers, animals and fun facts. Please ask a parent or teacher about that."
    return None


SYSTEMS = {"kids": KIDS, "en": ("You are a kind English teacher for Indian learners whose first language is Kannada or Hindi. "
          "Use very simple English (short sentences). When useful, add one short explanation in the learner language named below, and do not use any other language. "
          "If the learner writes a sentence with mistakes, show the corrected sentence first, then explain the mistake in one or two lines. "
          "Keep answers under 90 words. Only talk about learning English. Never ask for personal details."),
           "ai": ("You are a kind teacher who shows Indian beginners (first language Kannada or Hindi) how to use AI tools for study, jobs and daily life. "
          "The learner types a prompt. First answer the prompt helpfully in very simple English, under 80 words. "
          "Then add one line starting with 'Tip:' that says what was good about the prompt or how to make it better. "
          "Add one short explanation in the learner language named below, and do not use any other language. "
          "If the learner shares a password, OTP, bank or ID number, tell them not to share it and do not use it. "
          "Do not give medical, legal or investment advice; say to ask a professional. Never ask for personal details. Keep it safe for children.")}


def _read(name):
    with open(os.path.join(BASE, name), "r", encoding="utf-8") as f:
        return f.read()


def _ip(request):
    return (request.headers.get("x-forwarded-for") or (request.client.host if request.client else "x")).split(",")[0].strip()


RULES = (" Output format: return JSON with two fields. 'en' is your full answer in simple English (include any 'Tip:' line there). "
         "'kn' is one short explanation in {lang} only. Never mix scripts inside a sentence: 'en' has only English, 'kn' has only {lang} script. "
         "Write simple, natural spoken {lang} as in daily talk in Karnataka and India, using common words. Do not put English words or digits inside {lang} sentences (write numbers in {lang} words). "
         "Do not transliterate English into {lang} script except for common loan words such as office, teacher and doctor. Each {lang} sentence must be under 12 words.")


def ask_ai(track, persona, text, level, lang):
    # Kids questions never leave this server for an external AI provider.
    if track == "kids":
        return {"en": "Let's practise together! Try letters, numbers, colours or animals in Kids Zone. For other questions, ask a parent or teacher.",
                "kn": ""}
    key = os.environ.get("GEMINI_API_KEY", "")
    if not key:
        return None
    body = {"system_instruction": {"parts": [{"text": SYSTEMS[track] + " Your name is " + persona + ". Learner level: " + level + ". Add the short explanation in " + lang + " script." + RULES.replace("{lang}", lang)}]},
            "contents": [{"role": "user", "parts": [{"text": text[:600]}]}],
            "generationConfig": {"temperature": 0.3, "responseMimeType": "application/json",
                                 "responseSchema": {"type": "OBJECT", "properties": {"en": {"type": "STRING"}, "kn": {"type": "STRING"}}, "required": ["en", "kn"]}}}
    if track == "kids":
        body["safetySettings"] = [{"category": c, "threshold": "BLOCK_LOW_AND_ABOVE"} for c in ("HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT")]
    for m in MODELS:
        try:
            req = urllib.request.Request(
                "https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent?key=%s" % (m, key),
                data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=25) as r:
                j = json.loads(r.read())
            out = j["candidates"][0]["content"]["parts"][0]["text"]
            try:
                d = json.loads(out)
                if isinstance(d, dict) and (d.get("en") or d.get("kn")):
                    return {"en": str(d.get("en") or "").strip(), "kn": str(d.get("kn") or "").strip()}
            except Exception:
                pass
            return out
        except Exception:
            continue
    return ""


def install(app):
    _n0 = len(app.router.routes)
    @app.get("/english", response_class=HTMLResponse)
    async def learn_english():
        return HTMLResponse(_read("learn_en.html"))

    @app.get("/ai", response_class=HTMLResponse)
    async def learn_ai():
        return HTMLResponse(_read("learn_ai.html"))

    @app.get("/manifest.webmanifest")
    async def learn_manifest():
        return Response(MANIFEST, media_type="application/manifest+json")

    @app.get("/sw.js")
    async def learn_sw():
        return Response(SW, media_type="application/javascript", headers={"Cache-Control": "no-cache"})

    @app.get("/icon-192.png")
    async def learn_i192():
        return Response(ICON192, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/icon-512.png")
    async def learn_i512():
        return Response(ICON512, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/api/learn/status")
    async def learn_status():
        return {"ai": bool(os.environ.get("GEMINI_API_KEY"))}

    @app.get("/api/learn/tts")
    async def learn_tts(lang: str = "kn", text: str = ""):
        text = text[:200]
        if lang not in ("kn", "hi", "en") or not text.strip():
            return Response("bad", status_code=400)
        k = (lang, text)
        if k in TTS_CACHE:
            return Response(TTS_CACHE[k], media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
        try:
            u = "https://translate.google.com/translate_tts?ie=UTF-8&client=tw-ob&tl=%s&q=%s" % (lang, quote(text))
            rq = urllib.request.Request(u, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://translate.google.com/"})
            data = urllib.request.urlopen(rq, timeout=10).read()
            if len(TTS_CACHE) > 300:
                TTS_CACHE.clear()
            TTS_CACHE[k] = data
            return Response(data, media_type="audio/mpeg", headers={"Cache-Control": "public, max-age=86400"})
        except Exception:
            return Response("tts unavailable", status_code=502)

    @app.post("/api/learn/ask")
    async def learn_ask(request: Request):
        ip = _ip(request)
        now = time.time()
        hits = [t for t in RATE.get(ip, []) if now - t < 3600]
        if len(hits) >= 40:
            return JSONResponse({"reply": "Too many questions this hour. Please come back later."}, status_code=429)
        hits.append(now)
        RATE[ip] = hits
        if len(RATE) > 5000:
            RATE.clear()
        try:
            raw = await request.body()
            d = json.loads(raw[:4000])
        except Exception:
            return JSONResponse({"reply": "Please try again."}, status_code=400)
        text = str(d.get("text", "")).strip()[:600]
        if not text:
            return JSONResponse({"reply": "Type a question first."})
        track = d.get("track") if d.get("track") in ("ai", "kids") else "en"
        if track == "kids":
            return JSONResponse({"reply": "Let's practise together! Try letters, numbers, colours or animals in Kids Zone. For other questions, ask a parent or teacher.",
                                 "en": "Let's practise together! Try letters, numbers, colours or animals in Kids Zone. For other questions, ask a parent or teacher.",
                                 "kn": "", "mode": "curated"})
        g = _guard(track, text)
        if g:
            return JSONResponse({"reply": g})
        persona = "Arjun" if d.get("persona") == "Arjun" else "Anaya"
        lang = "Hindi" if d.get("lang") == "hi" else "Kannada"
        level = str(d.get("level", "Beginner"))[:20]
        import asyncio
        reply = await asyncio.get_event_loop().run_in_executor(None, ask_ai, track, persona, text, level, lang)
        if reply is None:
            return JSONResponse({"reply": "Ask teacher is not switched on yet."})
        if not reply:
            return JSONResponse({"reply": "The teacher is busy. Please try again in a minute."})
        if isinstance(reply, dict):
            en, kn = reply.get("en", ""), reply.get("kn", "")
            return JSONResponse({"reply": (en + ("\n" + kn if kn else "")).strip(), "en": en, "kn": kn})
        return JSONResponse({"reply": reply})
    # Run before the site's catch-all /{seo_slug} route.
    _new = app.router.routes[_n0:]
    del app.router.routes[_n0:]
    app.router.routes[0:0] = _new
