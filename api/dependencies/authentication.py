
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

from jwt.exceptions import ExpiredSignatureError, InvalidTokenError
from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from api.utils.auth.hasher import verify_password
from api.utils.auth.scopes.fields.boolean_field import AdministratorScope
from api.utils.auth.scopes.scope_manager import ScopeManager
from api.utils.auth.token_const import private_key, ALGORITHM
from db.session.session import AsyncSessionDep
from db.models.users import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    # TODO
    scopes=ScopeManager().get_openapi_scope_docs()
)

ADMIN_SCOPE_VALUE = AdministratorScope(granted=True).get_scope_values()

class RedactedUserInDB(BaseModel):
    username: str
    disabled: bool
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

async def get_user_from_db(session: AsyncSession, username: str):
    try:
        # Omit sensitive data
        db_user = (await session.exec(select(User).where(User.username == username))).one()
        return RedactedUserInDB(username=db_user.username, disabled=db_user.disabled)
    except NoResultFound:
        return None


async def authenticate_user_from_db(session: AsyncSession, username: str, password: str) -> User | None:
    try:
        db_user = (await session.exec(select(User).where(User.username == username))).one()

        if verify_password(password, db_user.hash):
            return db_user
        return None
    except NoResultFound:
        return None


async def authorise_current_user(token: Annotated[str, Depends(oauth2_scheme)], security_scopes: SecurityScopes, session: AsyncSessionDep) -> RedactedUserInDB:
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
        RedactedUserInDB: The user that has been authorised to access the endpoint with sensitive data removed.
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
        required_scope: str = payload.get("scope", "")
        token_scopes = required_scope.split(" ")
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
        for required_scope in security_scopes.scopes:
            if required_scope not in token_data.scopes:
                raise credentials_exception
    
    return user