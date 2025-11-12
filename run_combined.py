from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

# Keep CSR/Max app at ROOT (its /login, /api/..., etc.)
from Max_app import app as csr_app, ensure_default_csr

# Mount the other app (PIN) under /pin
from app import app as pin_app

# Combined WSGI app: root -> Max_app, /pin -> other app
application = DispatcherMiddleware(csr_app, {
    "/pin": pin_app
})

if __name__ == "__main__":
    # make sure the default CSR user exists
    ensure_default_csr()
    # run on the port your frontend expects
    run_simple("0.0.0.0", 5050, application, use_reloader=True, use_debugger=True)
