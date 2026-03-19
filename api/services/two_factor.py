from typing import Annotated

from fastapi import Security

from api.dependencies.auth.authentication import RedactedUserInDB, authorise_current_redacted_user, get_user_from_db
from api.dependencies.auth.responses import bad_credentials_exception, two_factor_disabled_exception, two_factor_enabled_exception
from api.dependencies.auth.scopes import two_factor_setup_verification_scope_manager
from api.utils.auth.two_factor_auth.totp import decrypt_otp_key
from db.session.session import AsyncSessionDep


async def check_2fa_disabled(user_from_token: RedactedUserInDB, session: AsyncSessionDep):
    user = await get_user_from_db(session, user_from_token.username)
    if user is None:
        raise bad_credentials_exception
    if user.two_factor_enabled:
        raise two_factor_enabled_exception

async def check_2fa_enabled(user_from_token: RedactedUserInDB, session: AsyncSessionDep):
    user = await get_user_from_db(session, user_from_token.username)
    if user is None:
        raise bad_credentials_exception
    if not user.two_factor_enabled:
        raise two_factor_disabled_exception

async def get_plain_2fa_key_from_redacted_user(
    current_user: Annotated[RedactedUserInDB, Security(authorise_current_redacted_user, scopes=two_factor_setup_verification_scope_manager.get_scope_array())], 
    session: AsyncSessionDep):
    await check_2fa_disabled(current_user, session)
    unredacted_user = await get_user_from_db(session=session, username=current_user.username)
    
    plain_2fa_secret = decrypt_otp_key(unredacted_user.two_factor_secret)
    
    return plain_2fa_secret