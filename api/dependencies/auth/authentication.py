
from typing import Annotated

import jwt
from fastapi import Depends, Form, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel, Field
from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.utils.auth.hasher import verify_password
from api.utils.auth.scopes.fields.boolean_field import AdministratorScope
from api.utils.auth.scopes.scope_manager import ScopeManager
from api.utils.auth.token_const import private_key, ALGORITHM
from api.utils.auth.two_factor_auth.totp import get_cur_totp_for_key
from db.session.session import AsyncSessionDep
from db.models.users import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    # TODO
    scopes=ScopeManager().get_openapi_scope_docs()
)

ADMIN_SCOPE_VALUE = AdministratorScope(granted=True).get_scope_values()

MAX_FAILED_LOGIN_ATTEMPTS = 5

class RedactedUserInDB(BaseModel):
    username: str
    disabled: bool
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
    
class TOTPCode(BaseModel):
    totp: str = Field(pattern=r'^\d{8}$')
    
# TOTPUrlEncodedForm = Annotated[Annotated[str, Field(pattern=r'^\d{8}$')], Form()]
    
async def get_user_from_db(session: AsyncSession, username: str):
    try:
        db_user = (await session.exec(select(User).where(User.username == username))).one()
        return db_user
    except NoResultFound:
        return None

async def get_redacted_user_from_db(session: AsyncSession, username: str):
    user = await get_user_from_db(session, username)
    if user is not None:
        return RedactedUserInDB(username=user.username, disabled=user.disabled)


async def authenticate_user_from_db_without_totp(session: AsyncSession, username: str, password: str) -> User | None:
    db_user = await get_user_from_db(session, username)
    
    if db_user is None:
        return None

    if verify_password(password, db_user.hash):
        return db_user
    # TODO: Revisit restricting accounts when failed attempts occur
    # else:
    #     db_user.failed_attempts += 1
    #     if db_user.failed_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
    #         db_user.disabled = True
    #     await session.commit()
    #     return None
    
async def authenticate_user_from_db_with_totp(session: AsyncSession, username: str, password: str, totp: str) -> User | None:
    db_user = await get_user_from_db(session, username)
    cur_totp = get_cur_totp_for_key(db_user.two_factor_secret)

    if db_user is not None and verify_password(password, db_user.hash) \
        and cur_totp == totp and not verify_password(totp, db_user.last_two_factor):
        return db_user


async def authorise_current_redacted_user(token: Annotated[str, Depends(oauth2_scheme)], security_scopes: SecurityScopes, session: AsyncSessionDep):
   """
    Identical to ``authorise_current_full_user()``, but redacts sensitive information to protect against leaks. 
    Should be preferred when these fields are not needed to reduce potential for vulnerabilities.
    """
   full_user = await authorise_current_full_user(token, security_scopes, session)
   return RedactedUserInDB(username=full_user.username, disabled=full_user.disabled)

async def authorise_current_full_user(token: Annotated[str, Depends(oauth2_scheme)], security_scopes: SecurityScopes, session: AsyncSessionDep):
    """
    Authorises the current user against the specified security scopes via their provided token. 
    If the token is valid, the user is validated to currently exist and not be disabled at the point of the API call, 
    subsequently validating if the user has all required security scopes (admin scopes bypass this requirement).
    
    A disabled user is equivalent to always having insufficient scopes for an endpoint requiring authorisation.

    Args:
        token (Annotated[str, Depends(oauth2_scheme)]): The token to validate and use for endpoint authorisation.
        security_scopes (SecurityScopes): The required scopes that must *all* be met for authorisation.
        session (AsyncSessionDep): A session for the relevant database to check for the user's existence and account state.

    Raises:
        credentials_exception: If the user is not authorised to access the endpoint or does not exist.

    Returns:
        User: The user that has been authorised to access the endpoint.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Find the relevant user from the token
        payload = jwt.decode(token, private_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        
        # extract the scopes from the token to use for authentication
        raw_token_scopes: str = payload.get("scope", "")
        token_scopes = raw_token_scopes.split(" ")
        token_data = TokenData(scopes=token_scopes, username=username)
    
    except InvalidTokenError, ExpiredSignatureError:
        raise credentials_exception
    
    # Verify that there is the specified user for the token in the DB
    user = await get_user_from_db(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    
    # A disabled user cannot access any authenticated endpoint
    if user.disabled:
        raise credentials_exception
    
    
    # Only check for the required scopes if the token does not provide admin access
    if token_data.scopes != ADMIN_SCOPE_VALUE:
        # Verify that the token grants the required scopes for the endpoint
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise credentials_exception
    
    return user