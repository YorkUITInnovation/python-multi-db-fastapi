from typing import Optional
from fastapi import Header, HTTPException
from .config import API_KEYS

async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-KEY")):
    if not API_KEYS:
        raise HTTPException(status_code=500, detail="API key(s) not configured")
    if x_api_key is None or x_api_key not in API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return True
