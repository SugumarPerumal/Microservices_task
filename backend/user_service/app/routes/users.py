from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserProfileCreate, UserProfileResponse
from app.services.user_service import create_user_profile
from app.services.user_service import get_user_profile
from app.schemas.user import UserProfileUpdate
from app.services.user_service import update_user_profile

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post(
    "/profile",
    response_model=UserProfileResponse,
    status_code=status.HTTP_201_CREATED
)
def create_profile(
    profile_data: UserProfileCreate,
    auth_user_id: int = Header(..., alias="X-Authenticated-User-Id"),
    db: Session = Depends(get_db)
):
    # Temporary development placeholder.
    # We will replace this with the authenticated user ID
    # obtained from JWT validation before testing this endpoint.
    #auth_user_id = None

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
    response_model=UserProfileResponse
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
    response_model=UserProfileResponse
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