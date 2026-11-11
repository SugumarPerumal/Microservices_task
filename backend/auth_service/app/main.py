from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.user import User
from app.routes.auth import router as auth_router
from app.models.refresh_token import RefreshToken

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Authentication Service",
    description="Authentication microservice for E-Commerce Platform",
    version="1.0.0"
)


# Register authentication routes
app.include_router(auth_router)


@app.get("/")
def root():
    return {
        "message": "Authentication Service is running"
    }