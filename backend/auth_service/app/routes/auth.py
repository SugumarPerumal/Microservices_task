from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import RegisterRequest, UserResponse, LoginRequest, TokenResponse, RefreshTokenRequest, ChangePasswordRequest
from app.services.security import hash_password, verify_password, hash_refresh_token
from app.models.refresh_token import RefreshToken
from app.services.token import (
    create_access_token,
    create_refresh_token,
    get_token_expiry, verify_token
)
from jwt.exceptions import InvalidTokenError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.password_service import change_user_password
import jwt

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

bearer_scheme = HTTPBearer()

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register_user(
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):

    # Check whether email already exists
    existing_user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Hash the user's password
    hashed_password = hash_password(user_data.password)

    # Create a new user object
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hashed_password
    )

    # Save user into database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def login_user(
    user_data: LoginRequest,
    db: Session = Depends(get_db)
):

    # Find user using email
    user = db.query(User).filter(
        User.email == user_data.email
    ).first()

    # Check whether user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Verify password
    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Check account status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Generate tokens
    access_token = create_access_token(user.id)

    refresh_token = create_refresh_token(user.id)

    # Hash refresh token before storing
    hashed_refresh_token = hash_refresh_token(refresh_token)

    # Create refresh token database record
    token_record = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh_token,
        expires_at=get_token_expiry(refresh_token)
    )

    # Save refresh token record
    db.add(token_record)
    db.commit()

    # Return tokens
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )

@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
def refresh_access_token(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    # Verify the refresh token
    try:
        payload = verify_token(token_data.refresh_token)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Ensure this is a refresh token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user ID from token
    user_id = int(payload["sub"])

    # Hash the submitted refresh token
    token_hash = hash_refresh_token(token_data.refresh_token)

    # Find the stored refresh token
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.user_id == user_id
    ).with_for_update().first()

    # Check whether token exists and is valid
    if not stored_token or stored_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or is invalid"
        )

    # Check whether user exists and is active
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive or unavailable"
        )

    # Revoke the old refresh token
    stored_token.is_revoked = True

    # Generate new tokens
    new_access_token = create_access_token(user.id)

    new_refresh_token = create_refresh_token(user.id)

    # Hash the new refresh token
    new_token_hash = hash_refresh_token(new_refresh_token)

    # Store the new refresh token
    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=new_token_hash,
        expires_at=get_token_expiry(new_refresh_token)
    )

    db.add(new_token_record)

    # Save revocation and new token together
    db.commit()

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token
    )

@router.post(
    "/logout",
    status_code=status.HTTP_200_OK
)
def logout_user(
    token_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):

    # Verify refresh token
    try:
        payload = verify_token(token_data.refresh_token)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )

    # Ensure token type is refresh
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Get user ID
    user_id = int(payload["sub"])

    # Hash submitted token
    token_hash = hash_refresh_token(token_data.refresh_token)

    # Find token record
    stored_token = db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.user_id == user_id
    ).with_for_update().first()

    # Check whether token exists and is not revoked
    if not stored_token or stored_token.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token already revoked or invalid"
        )

    # Revoke token
    stored_token.is_revoked = True

    # Save changes
    db.commit()

    return {
        "message": "Logout successful"
    }

@router.get("/validate")
def validate_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
):

    # Extract token from Authorization header
    token = credentials.credentials

    # Verify JWT signature and expiration
    try:
        payload = verify_token(token)

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired access token"
        )

    # Ensure the token is an access token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )

    # Extract user ID
    try:
        user_id = int(payload["sub"])

    except (KeyError, TypeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )

    # Find user in database
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    # Check account availability
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is unavailable"
        )

    # Return authenticated user information
    return {
        "valid": True,
        "user_id": user.id,
        "email": user.email,
        "is_active": user.is_active
    }


@router.post("/change-password")
def change_password(
    password_data: ChangePasswordRequest,
    credentials: HTTPAuthorizationCredentials = Depends(
        HTTPBearer()
    ),
    db: Session = Depends(get_db),
):

    # Step 1: Validate the JWT
    try:
        payload = verify_token(credentials.credentials)

        if not isinstance(payload, dict):
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
            )

        if payload.get("type") != "access":
            raise HTTPException(
                status_code=401,
                detail="Invalid access token",
            )

        user_id = int(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError, TypeError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired access token",
        )


    # Step 2: Validate new password using the
    # existing registration password rules.
    # Reuse your existing password validator here.

    # Step 3: Call the password service
    result = change_user_password(
        db=db,
        user_id=user_id,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    # Step 4: Handle possible results
    if result == "USER_NOT_FOUND":
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
        )

    if result == "INVALID_CURRENT_PASSWORD":
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    if result == "SAME_PASSWORD":
        raise HTTPException(
            status_code=400,
            detail="New password must be different",
        )

    return {
        "message": "Password changed successfully"
    }
