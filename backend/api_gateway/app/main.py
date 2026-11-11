
from fastapi import FastAPI, Request

from app.config.settings import settings
from app.services.proxy import forward_request
from app.services.proxy import (
    forward_request,
    validate_access_token
)


app = FastAPI(
    title="API Gateway",
    description="Central entry point for the E-Commerce Microservices",
    version="1.0.0"
)


@app.get("/")
def root():
    return {"message": "API Gateway is running"}



@app.get("/auth/{path:path}")
@app.post("/auth/{path:path}")
@app.put("/auth/{path:path}")
@app.patch("/auth/{path:path}")
@app.delete("/auth/{path:path}")
async def user_gateway(path: str, request: Request):
    user_data = await validate_access_token(request)

    return await forward_request(
        request=request,
        target_url=settings.USER_SERVICE_URL,
        path=f"users/{path}",
        authenticated_user_id=user_data["user_id"]
    )


@app.get("/users/{path:path}")
@app.post("/users/{path:path}")
@app.put("/users/{path:path}")
@app.patch("/users/{path:path}")
@app.delete("/users/{path:path}")
async def user_gateway(path: str, request: Request):
    return await forward_request(
        request=request,
        target_url=settings.USER_SERVICE_URL,
        path=f"users/{path}"
    )
