
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
from api.utils.auth.scopes.management import ScopeManager
from api.utils.auth.token_const import private_key, ALGORITHM
from db.session.session import AsyncSessionDep
from db.models.users import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    # TODO
    scopes=ScopeManager().get_openapi_scope_docs()
)

ADMIN_SCOPE_VALUE = ScopeManager(admin=True).get_scope_array()

class UserInDB(BaseModel):
    username: str
    
class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []

async def get_user_from_db(session: AsyncSession, username: str):
    try:
        db_user = (await session.exec(select(User).where(User.username == username))).one()
        return UserInDB(username=db_user.username)
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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], security_scopes: SecurityScopes, session: AsyncSessionDep):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
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
    # Only check for the required scopes if the token does not provide admin access
    if token_data.scopes != ADMIN_SCOPE_VALUE:
        # Verify that the token grants the required scopes for the endpoint
        for required_scope in security_scopes.scopes:
            if required_scope not in token_data.scopes:
                raise credentials_exception
    return user