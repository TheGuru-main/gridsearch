"""
BubbleJumbo middleware for the combined OpenBox + Fantasy backend.

Rules:
  1. Primary user sessions are NEVER trapped. Only notified.
  2. Only suspicious sessions (attacker screens) get the grid.
  3. Phishing screens redirecting back from external links can be trapped.
  4. Fail-open: BubbleJumbo unreachable → app keeps working.
  5. Fail-closed: BubbleJumbo says "trap" → grid served.
"""
import uuid
from fastapi import Request, APIRouter
from fastapi.responses import JSONResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware
from bubblejumbo_client import bj_client


# Static, health, docs, and our own bridge endpoints never need inspection.
SKIP_PATHS = (
    "/static",
    "/favicon.ico",
    "/health",
    "/docs",
    "/openapi.json",
    "/api/bj/",
)

SENSITIVE_PATHS = (
    "/api/session",
    "/api/wallet",
    "/api/upload",
    "/api/download",
    "/api/messages",
    "/api/groups",
    "/api/fantasy",
    "/api/purchase",
    "/api/account",
    "/api/admin",
    "/api/auth",
    "/api/health",
    "/api/openbox",
    "/login",
    "/register",
    "/admin",
    "/.env",
    "/config",
)

class BubbleJumboMiddleware(BaseHTTPMiddleware):
    """
    Wraps every request. Determines caller identity, feeds signals to
    BubbleJumbo, and enforces the response.
    """

    async def dispatch(self, request: Request, call_next):
    # ---- debug log ----
    import os, time as _t
    if os.environ.get("BJ_DEBUG", "1") == "1":
        try:
            with open("/tmp/bj_debug.log", "a") as f:
                f.write(f"{_t.time()} {request.method} {request.url.path}\n")
        except Exception:
            pass

    path = request.url.path

    # Skip paths that never need inspection
    if path.startswith(SKIP_PATHS):
        return await call_next(request)

    # Resolve session
    session_id = request.cookies.get("snm_session")
    new_session = not session_id
    if not session_id:
        session_id = "snm-" + uuid.uuid4().hex

    kind = request.cookies.get("snm_kind", "primary")
    if kind not in ("primary", "suspicious"):
        kind = "primary"

    is_phishing = self._is_phishing(request)

    if not (path.startswith(SENSITIVE_PATHS) or is_phishing):
        response = await call_next(request)
        self._set_cookies(response, session_id, kind, new_session)
        return response

    body = b""
    if request.method in ("POST", "PUT", "PATCH"):
        body = await request.body()

        async def receive():
            return {"type": "http.request", "body": body, "more_body": False}

        request._receive = receive

    payload = {
        "path": path,
        "verb": request.method,
        "body": body.decode("utf-8", errors="ignore")[:4096],
        "ip": request.client.host if request.client else "",
    }

    result = await bj_client.ingest(
        session_id=session_id,
        payload=payload,
        headers=dict(request.headers),
        is_phishing_screen=is_phishing,
    )
    data = result.get("data", {}) or {}

    if data.get("_fail_open"):
        response = await call_next(request)
        self._set_cookies(response, session_id, kind, new_session)
        return response

    action = data.get("action", "allow")
    status = data.get("status", "unknown")

    if action == "trap" and status == "trap":
        if kind == "primary" and not is_phishing:
            response = await call_next(request)
            self._set_cookies(response, session_id, kind, new_session)
            return response
        trap_html = await bj_client.trap_html(session_id)
        if trap_html:
            response = HTMLResponse(content=trap_html, status_code=403)
            self._set_cookies(response, session_id, kind, new_session)
            return response
        return JSONResponse(
            status_code=403,
            content={"error": "Security verification required."},
        )

    response = await call_next(request)
    if action == "notify":
        response.headers["X-BJ-Notice"] = "1"
    self._set_cookies(response, session_id, kind, new_session)
    return response

        # ─── Resolve session ───
        session_id = request.cookies.get("snm_session")
        new_session = not session_id
        if not session_id:
            session_id = "snm-" + uuid.uuid4().hex

        # ─── Session kind: primary (user) or suspicious (attacker) ───
        kind = request.cookies.get("snm_kind", "primary")
        if kind not in ("primary", "suspicious"):
            kind = "primary"

        # ─── Is this a phishing redirect flow? ───
        is_phishing = self._is_phishing(request)

        # ─── Only inspect sensitive paths or phishing flows ───
        if not (path.startswith(SENSITIVE_PATHS) or is_phishing):
            response = await call_next(request)
            self._set_cookies(response, session_id, kind, new_session)
            return response

        # ─── Capture body (without consuming it) ───
        body = b""
        if request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()

            async def receive():
                return {"type": "http.request", "body": body, "more_body": False}

            request._receive = receive

        payload = {
            "path": path,
            "verb": request.method,
            "body": body.decode("utf-8", errors="ignore")[:4096],
            "ip": request.client.host if request.client else "",
        }

        # ─── Ask BubbleJumbo ───
        result = await bj_client.ingest(
            session_id=session_id,
            payload=payload,
            headers=dict(request.headers),
            is_phishing_screen=is_phishing,
        )
        data = result.get("data", {}) or {}

        # ─── Fail open if BubbleJumbo is down ───
        if data.get("_fail_open"):
            response = await call_next(request)
            self._set_cookies(response, session_id, kind, new_session)
            return response

        action = data.get("action", "allow")
        status = data.get("status", "unknown")

        # ─── Trap logic ───
        if action == "trap" and status == "trap":
            # Safety net: never trap a primary user unless it's a phishing screen
            if kind == "primary" and not is_phishing:
                response = await call_next(request)
                self._set_cookies(response, session_id, kind, new_session)
                return response

            trap_html = await bj_client.trap_html(session_id)
            if trap_html:
                response = HTMLResponse(content=trap_html, status_code=403)
                self._set_cookies(response, session_id, kind, new_session)
                return response

            # If we can't fetch the trap HTML, still block — never let an attacker through
            return JSONResponse(
                status_code=403,
                content={"error": "Security verification required."},
            )

        # ─── Normal flow (allow or notify) ───
        response = await call_next(request)
        if action == "notify":
            response.headers["X-BJ-Notice"] = "1"
        self._set_cookies(response, session_id, kind, new_session)
        return response

    # ─── helpers ───
    def _is_phishing(self, request: Request) -> bool:
        """
        Detect whether this request is part of a phishing redirect flow.
        Triggers when:
          - query has ?bj_phishing=1 (set by our widget)
          - Referer comes from a domain outside our trust list
        """
        if request.query_params.get("bj_phishing") == "1":
            return True

        referer = request.headers.get("referer", "")
        if referer and "//" in referer:
            try:
                host = referer.split("/")[2]
            except IndexError:
                return False

            trusted = (
                "openbox",
                "localhost",
                "127.0.0.1",
                "onrender.com",
            )
            if host and not any(t in host for t in trusted):
                return True
        return False

    def _set_cookies(self, response, session_id: str, kind: str, new_session: bool):
        if new_session:
            response.set_cookie(
                "snm_session", session_id,
                httponly=True, samesite="lax", max_age=86400 * 7,
            )
            response.set_cookie(
                "snm_kind", kind,
                httponly=True, samesite="lax", max_age=86400 * 7,
            )


# ═══════════════════════════════════════════════════════
#  Bridge endpoints — mounted by app.py via app.include_router
#  The frontend widget polls /api/bj/notifications.
# ═══════════════════════════════════════════════════════
bj_bridge = APIRouter(prefix="/api/bj", tags=["bubblejumbo"])


@bj_bridge.get("/notifications")
async def get_notifications(request: Request):
    sid = request.cookies.get("snm_session")
    if not sid:
        return {"notifications": []}
    r = await bj_client.notifications(sid)
    return r.get("data", {"notifications": []})


@bj_bridge.get("/status")
async def get_status(request: Request):
    sid = request.cookies.get("snm_session")
    if not sid:
        return {"status": "unknown"}
    r = await bj_client.status(sid)
    return r.get("data", {"status": "unknown"})


@bj_bridge.post("/mark-suspicious")
async def mark_suspicious(request: Request):
    """
    Called by the frontend when a user lands on a phishing page and
    bounces back. Converts the session into a suspicious session so the
    trap can be served to that surface only.
    """
    sid = request.cookies.get("snm_session")
    if not sid:
        return {"ok": False}
    r = await bj_client.ingest(
        session_id=sid,
        payload={"path": "/phishing-detected", "verb": "POST", "body": "", "ip": ""},
        headers={},
        is_phishing_screen=True,
    )
    return r.get("data", {"ok": False})


@bj_bridge.post("/reset")
async def reset_session(request: Request):
    """Manual reset — clears trap status for the current session."""
    sid = request.cookies.get("snm_session")
    if not sid:
        return {"ok": False}
    r = await bj_client.reset(sid)
    return r.get("data", {"ok": False})