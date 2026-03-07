from datetime import timedelta
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, SecurityScopes

from jwt.exceptions import InvalidTokenError

from pydantic import BaseModel
from sqlalchemy.exc import NoResultFound, IntegrityError
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.responses import Response

from api.utils.auth.hasher import verify_password, get_password_hash
from api.utils.auth.scopes import ScopeManager, ScopeAccessLevel
from api.utils.auth.token import create_access_token
from api.utils.auth.token_const import private_key, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from db.session.session import AsyncSessionDep
from db.models.users import User

auth_router = APIRouter(prefix='/auth')


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    # TODO
    scopes={
        'songs:read': 'read song data',
        'songs:write': 'write song data'
    }
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserInDB(BaseModel):
    username: str


def get_mock_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)
    return None


async def get_user_from_db(session: AsyncSession, username: str):
    try:
        db_user = await session.exec(select(User).where(User.username == username)).one()
        return UserInDB(**db_user)
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


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: AsyncSessionDep):
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
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = await get_user_from_db(session, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@auth_router.post("/token")
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep
) -> Token:
    user = await authenticate_user_from_db(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # TODO: Provide specific scopes for each access level
    scopes = ScopeManager(song_access=ScopeAccessLevel.read, chart_access=ScopeAccessLevel.all,
                          chart_creator_access={ScopeAccessLevel.read, ScopeAccessLevel.write, ScopeAccessLevel.all}, cross_edit_access=True)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scope": str(scopes)}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@auth_router.post("/register")
async def register(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep
):
    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Provide both username and password",
        )

    pw_hash = get_password_hash(form_data.password)

    try:
        session.add(User(username=form_data.username, hash=pw_hash))
        await session.commit()
        # session.refresh(User(username=form_data.username, hash=hash))
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    return Response(status_code=status.HTTP_201_CREATED)