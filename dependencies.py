import os
from typing import Optional

from fastapi import Header, HTTPException, Request
from slowapi import Limiter


def _get_api_key(request: Request) -> str:
    return request.headers.get("X-API-Key", "anonymous")


# LIMITATION: in-memory storage resets on restart and is not shared across
# multiple workers/processes. Production would swap this for a Redis backend:
# Limiter(key_func=_get_api_key, storage_uri="redis://localhost:6379")
limiter = Limiter(key_func=_get_api_key)


def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Gate: confirms the caller has a valid API key.

    LIMITATION: this is a single shared key — there is no per-user identity.
    Every authenticated caller can read and write every session regardless of
    who created it. Production would replace this with per-user API keys or
    JWTs, add a users table, and scope all queries with WHERE user_id = ?.
    """
    if x_api_key is None:
        raise HTTPException(status_code=401, detail="Missing API key")
    if x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
