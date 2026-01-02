from typing import Optional
from fastapi import HTTPException, status, Security
from fastapi.security.api_key import APIKeyHeader
from .config import API_KEYS

# Define the API key header security scheme (this registers the scheme in OpenAPI)
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)

async def verify_api_key(api_key: Optional[str] = Security(api_key_header)):
    """Verify the incoming X-API-KEY header against configured keys.

    Using Security(api_key_header) ensures the OpenAPI schema includes a single
    API key security scheme. Routes that depend on this function will require
    the header and Swagger UI will show a single "Authorize" input.
    """
    if not API_KEYS:
        raise HTTPException(status_code=500, detail="API key(s) not configured")
    if api_key is None or api_key not in API_KEYS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing API key")
    return True
