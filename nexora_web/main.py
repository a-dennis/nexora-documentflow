"""Entry point: the app plus the payment fixes. Start with `uvicorn main:app`."""
import app as _appmod
import payfix

payfix.install(vars(_appmod))
try:
    import stats
    stats.install(vars(_appmod))
except Exception as _e:
    print("STATS_INSTALL_FAILED", repr(_e))
try:
    import admin
    admin.install(vars(_appmod))
except Exception as _e:
    print("ADMIN_INSTALL_FAILED", repr(_e))
try:
    import pwa
    pwa.install(vars(_appmod))
except Exception as _e:
    print("PWA_INSTALL_FAILED", repr(_e))
try:
    import chatbot
    chatbot.install(vars(_appmod))
except Exception as _e:
    print("BOT_INSTALL_FAILED", repr(_e))
try:
    import seo
    seo.install(vars(_appmod))
except Exception as _e:  # SEO layer must never take the site down
    print("SEO_INSTALL_FAILED", repr(_e))
app = _appmod.app

try:  # monitors often probe with HEAD; answer 200 instead of 405
    from fastapi import Response as _R
    _a = _appmod.app

    @_a.head("/health")
    async def _head_health():
        return _R(status_code=200)

    @_a.head("/")
    async def _head_root():
        return _R(status_code=200)
except Exception as _e:
    print("HEAD_ROUTE_FAILED", repr(_e))
