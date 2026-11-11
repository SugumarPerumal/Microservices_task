
from fastapi import FastAPI, Request

from app.config.settings import settings
from app.services.proxy import forward_request


app = FastAPI(
    title="API Gateway",
    description="Central entry point for the E-Commerce Microservices",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "API Gateway is running"}


@app.api_route(
    "/auth/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE"]
)
async def auth_gateway(path: str, request: Request):
    return await forward_request(
        request=request,
        target_url=settings.AUTH_SERVICE_URL,
        path=f"auth/{path}"
    )
