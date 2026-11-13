
from sqlalchemy.orm import Session

from app.models.user_profile import UserProfile
from app.schemas.user import UserProfileCreate, UserProfileUpdate


def create_user_profile(
    db: Session,
    auth_user_id: int,
    profile_data: UserProfileCreate
):
    existing_profile = (
        db.query(UserProfile)
        .filter(UserProfile.auth_user_id == auth_user_id)
        .first()
    )

    if existing_profile:
        return None

    new_profile = UserProfile(
        auth_user_id=auth_user_id,
        first_name=profile_data.first_name,
        last_name=profile_data.last_name,
        phone_number=profile_data.phone_number,
        date_of_birth=profile_data.date_of_birth
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


def get_user_profile(db: Session, auth_user_id: int):
    return (
        db.query(UserProfile)
        .filter(UserProfile.auth_user_id == auth_user_id)
        .first()
    )


def update_user_profile(
    db: Session,
    auth_user_id: int,
    profile_data: UserProfileUpdate
):
    profile = get_user_profile(db, auth_user_id)

    if not profile:
        return None

    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile
