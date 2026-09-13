"""
BubbleJumbo client — talks to the BubbleJumbo backend.
Fail-safe: if the backend is unreachable, the app keeps working.
Never blocks a legitimate user because of a BubbleJumbo outage.
"""
import os
import httpx
from typing import Dict, Optional

BUBBLEJUMBO_URL = os.environ.get(
    "BUBBLEJUMBO_URL",
    "https://bubblejumbosecurityv1.onrender.com"
)
BUBBLEJUMBO_TIMEOUT = float(os.environ.get("BUBBLEJUMBO_TIMEOUT", "2.5"))


class BubbleJumboClient:
    def __init__(self, base_url: str = BUBBLEJUMBO_URL, timeout: float = BUBBLEJUMBO_TIMEOUT):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    # ─── public API ───
    async def register_user(self, session_id: str) -> Dict:
        return await self._safe_post("/api/session/register", {"session_id": session_id})

    async def reset(self, session_id: str) -> Dict:
        return await self._safe_post("/api/session/reset", {"session_id": session_id})

    async def ingest(
        self,
        session_id: str,
        payload: Dict,
        headers: Dict,
        is_phishing_screen: bool = False,
    ) -> Dict:
        return await self._safe_post("/api/ingest", {
            "session_id": session_id,
            "payload": payload,
            "headers": headers,
            "is_phishing_screen": is_phishing_screen,
        })

    async def status(self, session_id: str) -> Dict:
        return await self._safe_get("/api/status", {"session_id": session_id})

    async def notifications(self, session_id: str) -> Dict:
        return await self._safe_get("/api/notifications", {"session_id": session_id})

    async def trap_html(self, session_id: str) -> Optional[str]:
        """Fetch the trap HTML for a session. Returns None if not trapped."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.get(
                    f"{self.base_url}/api/trap",
                    params={"session_id": session_id},
                )
                if r.status_code == 200:
                    return r.text
                return None
        except Exception:
            return None

    # ─── internals ───
    async def _safe_post(self, path: str, body: Dict) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.post(f"{self.base_url}{path}", json=body)
                try:
                    return {"ok": r.is_success, "status": r.status_code, "data": r.json()}
                except Exception:
                    return {"ok": r.is_success, "status": r.status_code, "data": {}}
        except Exception as e:
            return {
                "ok": False,
                "status": 0,
                "data": {"_error": str(e), "_fail_open": True},
            }

    async def _safe_get(self, path: str, params: Dict) -> Dict:
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as c:
                r = await c.get(f"{self.base_url}{path}", params=params)
                try:
                    return {"ok": r.is_success, "status": r.status_code, "data": r.json()}
                except Exception:
                    return {"ok": r.is_success, "status": r.status_code, "data": {}}
        except Exception as e:
            return {
                "ok": False,
                "status": 0,
                "data": {"_error": str(e), "_fail_open": True},
            }


bj_client = BubbleJumboClient()