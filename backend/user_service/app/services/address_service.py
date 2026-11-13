
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user_address import UserAddress
from app.models.user_profile import UserProfile
from app.schemas.address import AddressCreate, AddressUpdate


def get_profile(db: Session, auth_user_id: int):
    return db.scalar(
        select(UserProfile).where(
            UserProfile.auth_user_id == auth_user_id
        )
    )


def create_address(
    db: Session,
    auth_user_id: int,
    address_data: AddressCreate,
):
    profile = get_profile(db, auth_user_id)

    if profile is None:
        return None

    data = address_data.model_dump()

    if data["is_default"]:
        existing_addresses = db.scalars(
            select(UserAddress).where(
                UserAddress.user_profile_id == profile.id
            )
        ).all()

        for address in existing_addresses:
            address.is_default = False

    address = UserAddress(
        user_profile_id=profile.id,
        **data,
    )

    db.add(address)
    db.commit()
    db.refresh(address)

    return address


def get_addresses(db: Session, auth_user_id: int):
    profile = get_profile(db, auth_user_id)

    if profile is None:
        return None

    return db.scalars(
        select(UserAddress).where(
            UserAddress.user_profile_id == profile.id
        )
    ).all()


def update_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
    address_data: AddressUpdate,
):
    profile = get_profile(db, auth_user_id)

    if profile is None:
        return None

    address = db.scalar(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_profile_id == profile.id,
        )
    )

    if address is None:
        return None

    update_data = address_data.model_dump(exclude_unset=True)

    if update_data.get("is_default") is True:
        existing_addresses = db.scalars(
            select(UserAddress).where(
                UserAddress.user_profile_id == profile.id
            )
        ).all()

        for existing in existing_addresses:
            existing.is_default = False

    for key, value in update_data.items():
        setattr(address, key, value)

    db.commit()
    db.refresh(address)

    return address


def delete_address(
    db: Session,
    auth_user_id: int,
    address_id: int,
):
    profile = get_profile(db, auth_user_id)

    if profile is None:
        return False

    address = db.scalar(
        select(UserAddress).where(
            UserAddress.id == address_id,
            UserAddress.user_profile_id == profile.id,
        )
    )

    if address is None:
        return False

    db.delete(address)
    db.commit()

    return True
