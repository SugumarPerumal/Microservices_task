
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.services.security import hash_password, verify_password
from app.models.refresh_token import RefreshToken


def change_user_password(
    db: Session,
    user_id: int,
    current_password: str,
    new_password: str,
):
    # Step 1: Find the authenticated user
    user = db.scalar(
        select(User).where(User.id == user_id)
    )

    if user is None or not user.is_active:
        return "USER_NOT_FOUND"

    # Step 2: Verify the current password
    if not verify_password(
        current_password, user.password_hash
    ):
        return "INVALID_CURRENT_PASSWORD"

    # Step 3: Prevent reuse of the current password
    if verify_password(
        new_password, user.password_hash
    ):
        return "SAME_PASSWORD"

    # Step 4: Hash the new password
    user.password_hash = hash_password(new_password)

    # Step 5: Revoke all existing refresh tokens
    db.query(RefreshToken).filter(
        RefreshToken.user_id == user.id,
        RefreshToken.is_revoked.is_(False)
    ).update(
        {RefreshToken.is_revoked: True},
        synchronize_session=False
    )

    # Step 6: Save both changes in one transaction
    db.commit()

    return "SUCCESS"
