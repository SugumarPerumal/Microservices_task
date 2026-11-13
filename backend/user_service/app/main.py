
from fastapi import FastAPI

from app.db.database import Base, engine
from app.models.user_profile import UserProfile
from app.routes.users import router as users_router
from app.models.user_address import UserAddress
from app.routes.addresses import router as addresses_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="User Service",
    description="User management microservice for E-Commerce Platform",
    version="1.0.0"
)

app.include_router(users_router)
app.include_router(addresses_router)


@app.get("/")
def root():
    return {"message": "User Service is running"}
