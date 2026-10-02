"""Entry point: the app plus the payment fixes. Start with `uvicorn main:app`."""
import app as _appmod
import payfix

payfix.install(vars(_appmod))
app = _appmod.app
