
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.db.database import get_db
from app.schemas.address import (
    AddressCreate,
    AddressUpdate,
    AddressResponse,
)
from app.services import address_service


router = APIRouter(
    prefix="/users/addresses",
    tags=["User Addresses"],
)


def verify_internal_service(
    internal_secret: str = Header(
        ..., alias="X-Internal-Service-Secret"
    ),
):
    if not secrets.compare_digest(
        internal_secret,
        settings.INTERNAL_SERVICE_SECRET,
    ):
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )


@router.post(
    "",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(verify_internal_service)],
)
def create_address(
    address_data: AddressCreate,
    auth_user_id: int = Header(
        ..., alias="X-Authenticated-User-Id"
    ),
    db: Session = Depends(get_db),
):
    address = address_service.create_address(
        db, auth_user_id, address_data
    )

    if address is None:
        raise HTTPException(
            status_code=404,
            detail="User profile not found",
        )

    return address


@router.get(
    "",
    response_model=list[AddressResponse],
    dependencies=[Depends(verify_internal_service)],
)
def list_addresses(
    auth_user_id: int = Header(
        ..., alias="X-Authenticated-User-Id"
    ),
    db: Session = Depends(get_db),
):
    addresses = address_service.get_addresses(
        db, auth_user_id
    )

    if addresses is None:
        raise HTTPException(
            status_code=404,
            detail="User profile not found",
        )

    return addresses


@router.put(
    "/{address_id}",
    response_model=AddressResponse,
    dependencies=[Depends(verify_internal_service)],
)
def update_address(
    address_id: int,
    address_data: AddressUpdate,
    auth_user_id: int = Header(
        ..., alias="X-Authenticated-User-Id"
    ),
    db: Session = Depends(get_db),
):
    address = address_service.update_address(
        db, auth_user_id, address_id, address_data
    )

    if address is None:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )

    return address


@router.delete(
    "/{address_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(verify_internal_service)],
)
def delete_address(
    address_id: int,
    auth_user_id: int = Header(
        ..., alias="X-Authenticated-User-Id"
    ),
    db: Session = Depends(get_db),
):
    deleted = address_service.delete_address(
        db, auth_user_id, address_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Address not found",
        )
