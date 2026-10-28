import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

from .config import settings


@dataclass
class Session:
    session_id: str
    token: str
    agent: Any
    pending_approval : bool = False
    lock: asyncio.Lock = field(default_factory=asyncio.Lock)
    last_used: float = field(default_factory=time.time)


class SessionStore:
    """In-memory store. Fine for testing; swap for Redis later."""

    def __init__(self, ttl_seconds: int = settings.SESSION_TTL_SECONDS):
        self._sessions: dict[str, Session] = {}
        self._ttl = ttl_seconds

    def get(self, session_id: str | None) -> Session | None:
        if not session_id:
            return None
        return self._sessions.get(session_id)

    def add(self, session: Session) -> None:
        self._sessions[session.session_id] = session

    def delete(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)

    def purge_expired(self) -> None:
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if now - s.last_used > self._ttl]
        for sid in expired:
            del self._sessions[sid]


store = SessionStore()