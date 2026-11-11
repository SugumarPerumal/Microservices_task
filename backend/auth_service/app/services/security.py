from pwdlib import PasswordHash
import hashlib


# Create password hashing instance
password_hash = PasswordHash.recommended()


# Hash the original password
def hash_password(password: str) -> str:

    return password_hash.hash(password)


# Verify password against stored hash
def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:

    return password_hash.verify(
        plain_password,
        hashed_password
    )

# Hash refresh tokens before database storage
def hash_refresh_token(token: str) -> str:

    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()