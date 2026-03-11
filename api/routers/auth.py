from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette.responses import Response

from api.dependencies.authentication import Token, authenticate_user_from_db, authorise_current_user
from api.dependencies.scopes import get_scopes_for_role
from api.utils.auth.hasher import verify_password, get_password_hash
from api.utils.auth.scopes.management import ChartScopeField, DBReadSubScope, DBWriteSubScope, ScopeManager, SongScopeField, SdtBlobScopeField
from api.utils.auth.token import create_access_token
from api.utils.auth.token_const import TOKEN_EXPIRY_TIMEDELTA
from db.session.session import AsyncSessionDep
from db.models.users import User, UserAccess

auth_router = APIRouter(prefix='/auth')

s_test = ScopeManager(
    song_access=SongScopeField(read_access=DBReadSubScope(granted=True)),
    chart_access=ChartScopeField(read_access=DBReadSubScope(granted=True))
    ).get_scope_array()

@auth_router.post("/token")
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep
) -> Token:
    user = await authenticate_user_from_db(session, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    role_name = (await session.exec(select(UserAccess).where(UserAccess.id == user.access_level_id))).one()
    
    scopes = get_scopes_for_role(role_name.name)
    
    access_token = create_access_token(
        data={"sub": user.username, "scope": str(scopes)}, expires_delta=TOKEN_EXPIRY_TIMEDELTA
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
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    return Response(status_code=status.HTTP_201_CREATED)

# TODO
@auth_router.get("/test")
async def test(current_user: 
    Annotated[User, 
              Security(
                  authorise_current_user, 
                  scopes=s_test
                  )]):
    return current_user