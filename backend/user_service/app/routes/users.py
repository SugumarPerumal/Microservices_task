from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.database import get_db

from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
    UserProfileResponse
)

from app.services.user_service import (
    create_user_profile,
    get_user_profile,
    update_user_profile
)

import secrets

from app.config.settings import settings

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

def verify_internal_service(
    internal_secret: str = Header(
        ...,
        alias="X-Internal-Service-Secret"
    )
):
    if not secrets.compare_digest(
        internal_secret,
        settings.INTERNAL_SERVICE_SECRET
    ):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized service request"
        )

@router.post(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_internal_service)]
)
def create_profile(
    profile_data: UserProfileCreate,
    auth_user_id: int = Header(..., alias="X-Authenticated-User-Id"),
    db: Session = Depends(get_db)
):


    new_profile = create_user_profile(
        db=db,
        auth_user_id=auth_user_id,
        profile_data=profile_data
    )

    if not new_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User profile already exists"
        )

    return new_profile

@router.get(
    "/profile",
    response_model=UserProfileResponse,
    dependencies=[Depends(verify_internal_service)]
)
def read_profile(
    auth_user_id: int = Header(..., alias="X-Authenticated-User-Id"),
    db: Session = Depends(get_db)
):
    # Temporary placeholder; JWT authentication will supply this ID.
    #auth_user_id = None

    profile = get_user_profile(
        db=db,
        auth_user_id=auth_user_id
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return profile

@router.put(
    "/profile",
    response_model=UserProfileResponse,
    dependencies=[Depends(verify_internal_service)]
)
def update_profile(
    profile_data: UserProfileUpdate,
    auth_user_id: int = Header(..., alias="X-Authenticated-User-Id"),
    db: Session = Depends(get_db)
):
    # Temporary placeholder; JWT authentication will supply this ID.
    #auth_user_id = None

    updated_profile = update_user_profile(
        db=db,
        auth_user_id=auth_user_id,
        profile_data=profile_data
    )

    if not updated_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )

    return updated_profile