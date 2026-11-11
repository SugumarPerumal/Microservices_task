
import httpx

from fastapi import HTTPException, Request
from fastapi.responses import Response


async def forward_request(
    request: Request,
    target_url: str,
    path: str
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
            "connection"
        }
    }

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
