"""Entry point: the app plus the payment fixes. Start with `uvicorn main:app`."""
import app as _appmod
import payfix

payfix.install(vars(_appmod))
try:
    import seo
    seo.install(vars(_appmod))
except Exception as _e:  # SEO layer must never take the site down
    print("SEO_INSTALL_FAILED", repr(_e))
app = _appmod.app
