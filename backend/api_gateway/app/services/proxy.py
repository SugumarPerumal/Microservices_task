
import httpx

from fastapi import HTTPException, Request
from fastapi.responses import Response
from app.config.settings import settings

async def validate_access_token(request: Request):
    authorization = request.headers.get("Authorization")

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header is missing"
        )

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{settings.AUTH_SERVICE_URL}/auth/validate",
                headers={"Authorization": authorization}
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired access token"
            )

        return response.json()

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Authentication service is unavailable"
        )

async def forward_request(
    request: Request,
    target_url: str,
    path: str,
    authenticated_user_id: int | None = None
):
    # Build the destination URL
    url = f"{target_url.rstrip('/')}/{path}"

    # Copy request headers, excluding headers managed by HTTPX
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in {
            "host",
            "content-length",
            "connection",
            "x-authenticated-user-id"
        }
    }

    if authenticated_user_id is not None:
        headers["X-Authenticated-User-Id"] = str(authenticated_user_id)
        headers["X-Internal-Service-Secret"] = settings.INTERNAL_SERVICE_SECRET

    # Read the incoming request body
    body = await request.body()

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            service_response = await client.request(
                method=request.method,
                url=url,
                params=request.query_params,
                content=body,
                headers=headers
            )

        # Return the microservice's response to the client
        return Response(
            content=service_response.content,
            status_code=service_response.status_code,
            headers={
                "content-type": service_response.headers.get(
                    "content-type",
                    "application/json"
                )
            }
        )

    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="The requested service is currently unavailable"
        )
