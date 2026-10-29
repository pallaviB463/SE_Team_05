"""Academic Performance Analytics System (APAS) - reference build used as the system under test."""
import ssl

from flask import Flask, jsonify, redirect, request
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from . import api, web
from .db import close_db, connect, init_schema
from .security import hash_password

DEFAULT_CONFIG = {
    "DATABASE": "apas.db",
    "SESSION_COOKIE": "apas_session",
    "SESSION_IDLE_MINUTES": 30,
    "MAX_FAILED_LOGINS": 5,
    "LOCKOUT_MINUTES": 15,
    "AUDIT_MIN_RETENTION_MONTHS": 12,   # APAS-NF-004
    "ENFORCE_HTTPS": True,              # APAS-SR-003 (disable only for local development)
    "TRUST_PROXY": False,               # set True only behind a TLS-terminating reverse proxy
}


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(DEFAULT_CONFIG)
    app.config.update(config or {})
    app.config["DUMMY_HASH"] = hash_password("not-a-real-password")

    conn = connect(app.config["DATABASE"])
    init_schema(conn)
    conn.close()

    if app.config["TRUST_PROXY"]:
        # X-Forwarded-Proto is honoured only when a trusted proxy is configured (DEF-001).
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    app.register_blueprint(api.bp)
    app.register_blueprint(web.bp)
    app.teardown_appcontext(close_db)

    @app.before_request
    def require_https():
        if not app.config["ENFORCE_HTTPS"]:
            return None
        if request.is_secure:
            return None
        if request.method in ("GET", "HEAD"):
            return redirect(request.url.replace("http://", "https://", 1), code=301)
        resp = jsonify({"error": "HTTPS is required", "status": 403})
        resp.status_code = 403
        return resp

    @app.after_request
    def security_headers(resp):
        if app.config["ENFORCE_HTTPS"]:
            resp.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        resp.headers["X-Content-Type-Options"] = "nosniff"
        resp.headers["X-Frame-Options"] = "DENY"
        resp.headers["Referrer-Policy"] = "no-referrer"
        return resp

    @app.errorhandler(HTTPException)
    def http_error(err):
        if request.path.startswith("/api/"):
            resp = jsonify({"error": err.description, "status": err.code})
            resp.status_code = err.code
            return resp
        return err

    @app.errorhandler(Exception)
    def unexpected(err):
        # SAD 4.4.1: generic message, no internal details exposed.
        app.logger.exception("Unhandled error")
        return jsonify({"error": "An unexpected error occurred", "status": 500}), 500

    return app


def make_ssl_context(certfile, keyfile):
    """Server TLS context: TLS 1.2 is the minimum accepted protocol version (APAS-SR-003)."""
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    ctx.load_cert_chain(certfile, keyfile)
    return ctx
