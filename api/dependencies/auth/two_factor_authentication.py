from datetime import datetime

from sqlmodel import select

from api.dependencies.auth.authentication import RedactedUserInDB
from api.utils.auth.two_factor_auth.totp import decrypt_otp_key, totp_for_key_is_valid
from db.models.users import User
from db.session.session import AsyncSessionDep


async def verify_totp_for_token_user(user: RedactedUserInDB, session: AsyncSessionDep, totp: str, timestamp: datetime | None = None):        
    encrypted_2fa_secret = (await session.exec(select(User.two_factor_secret).where(User.username == user.username))).one()
    plain_2fa_secret = decrypt_otp_key(encrypted_2fa_secret)
    
    return totp_for_key_is_valid(plain_2fa_secret, totp, timestamp)