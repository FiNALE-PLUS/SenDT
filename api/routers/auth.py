from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import select
from starlette.responses import RedirectResponse, Response

from api.dependencies.authentication import TOTPCode, Token, authenticate_user_from_db, authenticate_user_from_db_with_totp, authorise_current_user
from api.dependencies.scopes import get_scopes_for_role
from api.utils.auth.hasher import verify_password, get_password_hash
from api.utils.auth.scopes.fields.boolean_field import VerifyTwoFactorScope
from api.utils.auth.scopes.fields.totp_access import TOTPScopeField, TOTPVerifySubScope
from api.utils.auth.scopes.scope_manager import ChartScopeField, ScopeManager, SongScopeField, SdtBlobScopeField
from api.utils.auth.scopes.fields import DBReadSubScope
from api.utils.auth.token import create_access_token
from api.utils.auth.token_const import TOKEN_EXPIRY_TIMEDELTA, TWO_FACTOR_TOKEN_EXPIRY_TIMEDELTA
from api.utils.auth.two_factor_auth.totp import get_cur_totp, get_otp_key
from db.session.session import AsyncSessionDep
from db.models.users import User, UserAccess

auth_router = APIRouter(prefix='/auth', tags=['Authentication'])

# TODO: Update the scope manager with the correct argument one migrated, and clean up the tanggle of endpoints with overlapping and incomplete goals
two_factor_verification_scopes = ScopeManager(totp_access=TOTPScopeField(verification_access=TOTPVerifySubScope(granted=True))).get_scope_array()

s_test = ScopeManager(
    song_access=SongScopeField(read_access=DBReadSubScope(granted=True)),
    chart_access=ChartScopeField(read_access=DBReadSubScope(granted=True))
    ).get_scope_array()

bad_credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@auth_router.post("/2fa-verification-token")
async def get_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep
) -> Token:
    """
    Generates a token containing a user's authorised scopes, based on their internal role. 
    If the user has not verified their 2FA codes for validity, the token will always contain only the scopes necessary to verify them.
    """
    if not user.two_factor_enabled:
        # TODO: `url_path_for` gets the path relative to the router, which omits the base '/api/v1'. find a way to include it without hardcoding
        # return RedirectResponse(url=auth_router.url_path_for('get_2fa_verification_token'))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="TOTP has not been verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # TODO: Complete and test 2FA workflow
    user = await authenticate_user_from_db(session, form_data.username, form_data.password)
    
    if user is None:
        raise bad_credentials_exception
    
    # user.last_two_factor = get_password_hash(totp)
    # await session.commit()
        
    
    access_role = (await session.exec(select(UserAccess).where(UserAccess.id == user.access_level_id))).one()
    scopes = get_scopes_for_role(access_role.name)
    
    access_token = create_access_token(
        data={"sub": user.username, "scope": str(scopes)}, expires_delta=TOKEN_EXPIRY_TIMEDELTA
    )
    return Token(access_token=access_token, token_type="bearer")


# TODO: Update scopes to add 2FA verification and 2FA access separately, then implement two-part login
@auth_router.post("/token")
async def get_full_token_via_two_factor_authentication(
    current_user: Annotated[User, Security(authorise_current_user, scopes=two_factor_verification_scopes)], totp: TOTPCode
    ):
    ...


@auth_router.post("/2fa-verify-token", name='get_2fa_verification_token')
async def get_two_factor_verification_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSessionDep
    ):
    """
    Generates a token containing a user's authorised scopes, based on their internal role. 
    If the user has not verified their 2FA codes for validity, the token will always contain only the scopes necessary to verify them.
    """
    user = await authenticate_user_from_db(session, form_data.username, form_data.password)
    if user is None:
        raise bad_credentials_exception
    if user.two_factor_enabled:
        # TODO: `url_path_for` gets the path relative to the router, which omits the base '/api/v1'. find a way to include it without hardcoding
        # return RedirectResponse(url=auth_router.url_path_for('get_2fa_verification_token'))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="TOTP has already been verified",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    scopes = two_factor_verification_scopes
    access_token = create_access_token(
        data={"sub": user.username, "scope": str(scopes)}, expires_delta=TWO_FACTOR_TOKEN_EXPIRY_TIMEDELTA
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
        session.add(User(username=form_data.username, hash=pw_hash, two_factor_secret=get_otp_key()))
        await session.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    return Response(status_code=status.HTTP_201_CREATED)

@auth_router.get("/2fa-qr")

# TODO
@auth_router.post("/2fa-verify")
async def verify_TOTP_validity(current_user: Annotated[User, Security(authorise_current_user, scopes=two_factor_verification_scopes)], totp: TOTPUrlEncodedForm):
    """
    Verifies that the user is able to give the correct TOTP for the secret saved by the server. 
    If successful, the user will be able to collect a token containing all scopes applicable to their role from the `token` endpoint.
    """
    
    
    
    return current_user