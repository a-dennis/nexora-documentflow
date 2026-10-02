"""Installable app (PWA): manifest, icons, service worker, offline page, install button.
Also serves /.well-known/assetlinks.json for a later Play Store (TWA) release when
ASSETLINKS_PACKAGE and ASSETLINKS_SHA256 are set in the environment."""
import io
import json
import os

_DONE = {"v": False}
_CACHE = {}
PURPLE = (124, 58, 237)
THEME = "#7c3aed"

SW_JS = r"""
const V = 'nexora-shell-v1';
const SHELL = ['/offline', '/icons/icon-192.png'];
self.addEventListener('install', e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== V).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  const r = e.request;
  if (r.method !== 'GET') return;
  const u = new URL(r.url);
  if (u.origin !== location.origin) return;
  if (/^\/(api|auth|buy|pay-thanks|admin)/.test(u.pathname)) return;
  if (r.mode === 'navigate') {
    e.respondWith(fetch(r).catch(() => caches.match('/offline')));
    return;
  }
  if (u.pathname.startsWith('/icons/')) {
    e.respondWith(caches.match(r).then(m => m || fetch(r)));
  }
});
"""

OFFLINE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex"><meta name="theme-color" content="#7c3aed"><title>Offline | Nexora</title>
<style>body{font-family:system-ui,Arial,sans-serif;margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;background:#f6f8fb;color:#0f172a;text-align:center;padding:24px}
.b{max-width:380px}h1{font-size:24px}p{color:#52637a}button{background:#7c3aed;color:#fff;border:0;border-radius:10px;padding:12px 20px;font-size:16px}</style></head>
<body><div class="b"><h1>You are offline</h1><p>Nexora needs an internet connection for its tools. Check your connection and try again.</p>
<button onclick="location.reload()">Try again</button></div></body></html>"""

HEAD_TAGS = ('<link rel="manifest" href="/manifest.webmanifest"><meta name="theme-color" content="#7c3aed">'
             '<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png"><meta name="mobile-web-app-capable" content="yes">'
             '<meta name="apple-mobile-web-app-capable" content="yes"><meta name="apple-mobile-web-app-title" content="Nexora">'
             '<meta name="apple-mobile-web-app-status-bar-style" content="default">')

INSTALL_JS = r"""<script>(function(){
if('serviceWorker' in navigator){window.addEventListener('load',function(){navigator.serviceWorker.register('/sw.js',{scope:'/'}).catch(function(){});});}
var standalone=window.matchMedia('(display-mode: standalone)').matches||navigator.standalone;
if(standalone)return;
try{if(localStorage.getItem('nxInstallHidden')==='1')return;}catch(e){}
var dp=null,btn=null;
function make(label){
  if(btn)return;
  btn=document.createElement('div');
  btn.id='nxInstall';
  btn.setAttribute('style','position:fixed;right:14px;bottom:14px;z-index:9999;display:flex;align-items:center;gap:6px;background:#7c3aed;color:#fff;border-radius:999px;box-shadow:0 6px 20px rgba(0,0,0,.25);font:600 14px system-ui,Arial,sans-serif');
  btn.innerHTML='<button id="nxInstallGo" style="all:unset;cursor:pointer;padding:11px 8px 11px 16px">'+label+'</button><button id="nxInstallX" aria-label="Dismiss" style="all:unset;cursor:pointer;padding:11px 14px 11px 4px;opacity:.8">&times;</button>';
  if(/^\/(english|ai)/.test(location.pathname)){btn.style.right='auto';btn.style.left='14px';}
  document.body.appendChild(btn);
  document.getElementById('nxInstallX').onclick=function(){btn.remove();try{localStorage.setItem('nxInstallHidden','1');}catch(e){}};
  document.getElementById('nxInstallGo').onclick=function(){
    if(dp){dp.prompt();dp.userChoice.then(function(){dp=null;btn.remove();});}
    else{alert('To install: tap the Share button, then "Add to Home Screen".');}
  };
}
window.addEventListener('beforeinstallprompt',function(e){e.preventDefault();dp=e;make('Install Nexora app');});
window.addEventListener('appinstalled',function(){if(btn)btn.remove();});
var ua=navigator.userAgent||'';
if(/iPhone|iPad|iPod/.test(ua)&&!window.MSStream){window.addEventListener('load',function(){setTimeout(function(){make('Install Nexora app');},2500);});}
})();</script>"""


def _font(size):
    from PIL import ImageFont
    for p in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def _icon(size, maskable=False):
    from PIL import Image, ImageDraw
    S = size * 4
    im = Image.new("RGBA", (S, S), PURPLE + (255,) if maskable else (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if not maskable:
        d.rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * 0.22), fill=PURPLE + (255,))
    # letter N drawn as polygons (no font dependency); maskable keeps it inside the 80% safe zone
    k = 0.30 if maskable else 0.36
    cx = cy = S / 2
    w = S * k * 2
    h = S * k * 2
    x0, y0 = cx - w / 2, cy - h / 2
    t = w * 0.24
    white = (255, 255, 255, 255)
    d.rectangle([x0, y0, x0 + t, y0 + h], fill=white)
    d.rectangle([x0 + w - t, y0, x0 + w, y0 + h], fill=white)
    d.polygon([(x0, y0), (x0 + t * 1.25, y0), (x0 + w, y0 + h), (x0 + w - t * 1.25, y0 + h)], fill=white)
    out = im.resize((size, size), Image.LANCZOS)
    b = io.BytesIO()
    out.save(b, "PNG")
    return b.getvalue()


def _shot(w, h):
    from PIL import Image, ImageDraw
    im = Image.new("RGB", (w, h), (246, 248, 251))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, int(h * 0.14)], fill=PURPLE)
    d.text((int(w * 0.05), int(h * 0.035)), "Nexora", font=_font(int(h * 0.06)), fill="white")
    lines = ["Free PDF Tools", "& Student Calculators", "", "Merge, split, compress, convert", "VTU SGPA, CGPA, percentage"]
    y = int(h * 0.26)
    for i, t in enumerate(lines):
        big = i < 2
        d.text((int(w * 0.06), y), t, font=_font(int(h * (0.075 if big else 0.04))), fill=(15, 23, 42) if big else (82, 99, 122))
        y += int(h * (0.1 if big else 0.07))
    for i, t in enumerate(["Merge PDF", "Compress PDF", "VTU SGPA"]):
        yy = int(h * 0.7) + i * int(h * 0.09)
        d.rounded_rectangle([int(w * 0.06), yy, int(w * 0.94), yy + int(h * 0.07)], radius=14, fill="white", outline=(227, 232, 240))
        d.text((int(w * 0.09), yy + int(h * 0.015)), t, font=_font(int(h * 0.035)), fill=(15, 23, 42))
    b = io.BytesIO()
    im.save(b, "PNG")
    return b.getvalue()


def _asset(name):
    if name not in _CACHE:
        if name == "icon-192.png":
            _CACHE[name] = _icon(192)
        elif name == "icon-512.png":
            _CACHE[name] = _icon(512)
        elif name == "maskable-512.png":
            _CACHE[name] = _icon(512, True)
        elif name == "apple-touch-icon.png":
            _CACHE[name] = _icon(180, True)
        elif name == "shot-wide.png":
            _CACHE[name] = _shot(1280, 720)
        elif name == "shot-narrow.png":
            _CACHE[name] = _shot(720, 1280)
    return _CACHE.get(name)


MANIFEST = {
    "id": "/",
    "name": "Nexora - Free PDF Tools & Student Calculators",
    "short_name": "Nexora",
    "description": "Free PDF tools (merge, split, compress, convert) and student calculators (VTU SGPA, CGPA, percentage), plus resume and HR tools.",
    "start_url": "/?source=pwa",
    "scope": "/",
    "display": "standalone",
    "orientation": "portrait",
    "background_color": "#ffffff",
    "theme_color": THEME,
    "lang": "en-IN",
    "dir": "ltr",
    "categories": ["productivity", "education", "utilities"],
    "icons": [
        {"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
        {"src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
        {"src": "/icons/maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
    "screenshots": [
        {"src": "/icons/shot-wide.png", "sizes": "1280x720", "type": "image/png", "form_factor": "wide", "label": "Nexora home"},
        {"src": "/icons/shot-narrow.png", "sizes": "720x1280", "type": "image/png", "form_factor": "narrow", "label": "Nexora on phone"},
    ],
    "shortcuts": [
        {"name": "PDF Tools", "url": "/pdf", "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}]},
        {"name": "Student Calculators", "url": "/students", "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}]},
        {"name": "Resume Builder", "url": "/resume-builder", "icons": [{"src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png"}]},
    ],
}


def install(g):
    if _DONE["v"]:
        return
    _DONE["v"] = True
    app = g["app"]
    from fastapi import Request
    from fastapi.responses import HTMLResponse, Response

    # merge: drop the older manifest/sw routes registered by learn.py so this module's
    # manifest + service worker (offline page, install button) are the single PWA setup.
    # learn.py's /icon-192.png and /icon-512.png routes stay in place.
    for _r in [r for r in app.router.routes if getattr(r, "path", None) in ("/manifest.webmanifest", "/sw.js")]:
        app.router.routes.remove(_r)

    @app.get("/manifest.webmanifest")
    async def manifest():
        return Response(json.dumps(MANIFEST), media_type="application/manifest+json", headers={"Cache-Control": "public, max-age=3600"})

    @app.get("/sw.js")
    async def sw():
        return Response(SW_JS, media_type="application/javascript", headers={"Cache-Control": "no-cache", "Service-Worker-Allowed": "/"})

    @app.get("/icons/{name}")
    async def icons(name: str):
        data = _asset(name)
        if not data:
            return Response("Not found", status_code=404)
        return Response(data, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

    @app.get("/offline")
    async def offline():
        return HTMLResponse("<!-- nx-seo -->" + OFFLINE, headers={"X-Robots-Tag": "noindex"})

    @app.get("/.well-known/assetlinks.json")
    async def assetlinks():
        pkg = os.environ.get("ASSETLINKS_PACKAGE", "").strip()
        fps = [x.strip() for x in os.environ.get("ASSETLINKS_SHA256", "").split(",") if x.strip()]
        if not (pkg and fps):
            return Response("Not found", status_code=404)
        data = [{"relation": ["delegate_permission/common.handle_all_urls"],
                 "target": {"namespace": "android_app", "package_name": pkg, "sha256_cert_fingerprints": fps}}]
        return Response(json.dumps(data), media_type="application/json")

    names = {"/manifest.webmanifest", "/sw.js", "/offline", "/.well-known/assetlinks.json"}
    rs = app.router.routes
    mine = [r for r in rs if getattr(r, "path", None) in names or str(getattr(r, "path", "")).startswith("/icons/")]
    for r in mine:
        rs.remove(r)
    rs[0:0] = mine

    @app.middleware("http")
    async def pwa_mw(request: Request, call_next):
        resp = await call_next(request)
        p = request.url.path
        if (request.method != "GET" or resp.status_code != 200 or p.startswith(("/api", "/admin", "/offline", "/icons", "/auth"))
                or "text/html" not in resp.headers.get("content-type", "")):
            return resp
        body = b"".join([c async for c in resp.body_iterator])
        try:
            doc = body.decode("utf-8")
            if "</head>" in doc and "</body>" in doc and "nxInstallGo" not in doc:
                if "rel=\"manifest\"" not in doc:
                    doc = doc.replace("</head>", HEAD_TAGS + "</head>", 1)
                i = doc.rfind("</body>")
                doc = doc[:i] + INSTALL_JS + doc[i:]
            out = doc.encode("utf-8")
        except Exception as e:
            print("PWA_ERR", p, repr(e))
            out = body
        h = {k: v for k, v in resp.headers.items() if k.lower() not in ("content-length", "content-type")}
        return Response(out, status_code=200, headers=h, media_type="text/html")
