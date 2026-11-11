from datetime import datetime, timedelta, timezone

import jwt

from app.config.settings import settings


# JWT algorithm
ALGORITHM = "HS256"


# Generate Access Token
def create_access_token(user_id: int) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Generate Refresh Token
def create_refresh_token(user_id: int) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire
    }

    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


# Verify JWT Token
def verify_token(token: str) -> dict:

    payload = jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload

def get_token_expiry(token: str) -> datetime:

    payload = verify_token(token)

    return datetime.fromtimestamp(
        payload["exp"],
        tz=timezone.utc
    )