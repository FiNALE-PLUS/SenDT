from datetime import datetime

from sqlmodel import select

from api.dependencies.auth.authentication import RedactedUserInDB
from api.dependencies.auth.responses import bad_credentials_exception
from api.utils.auth.hasher import verify_password
from api.utils.auth.two_factor_auth.totp import decrypt_otp_key, totp_for_key_is_valid
from db.models.users import User
from db.session.session import AsyncSessionDep


async def verify_totp_for_token_user(user: RedactedUserInDB, session: AsyncSessionDep, totp: str, timestamp: datetime | None = None):        
    secrets = (await session.exec(select(User.two_factor_secret, User.last_two_factor).where(User.username == user.username))).one()
    encrypted_secret = secrets[0]
    last_hashed_otp = secrets[1]
    plain_2fa_secret = decrypt_otp_key(encrypted_secret)
    
    # Prevent replay attacks by validating that the same TOTP isn't used more than once
    if last_hashed_otp is not None and verify_password(totp, last_hashed_otp):
        raise bad_credentials_exception
    
    key_valid = totp_for_key_is_valid(plain_2fa_secret, totp, timestamp)
    
    if not key_valid:
        raise bad_credentials_exception
    
    return key_valid