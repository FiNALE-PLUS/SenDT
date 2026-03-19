from typing import Annotated

from fastapi import APIRouter, Response, Security, status
from sqlmodel import select

from api.dependencies.admin.request_body import HarmfulIPAddressBanBody
from api.dependencies.auth.authentication import RedactedUserInDB, authorise_current_redacted_user
from api.dependencies.auth.responses import bad_credentials_exception
from api.utils.auth.scopes.fields.boolean_field import AdministratorScope
from api.utils.auth.scopes.scope_manager import ScopeManager
from db.models.api.ip_blacklist import BannedIPAddress
from db.models.users import User
from db.session.session import AsyncSessionDep
from utils.timestamps.default_timestamps import get_utc_now

admin_scopes = ScopeManager(admin=AdministratorScope(granted=True))

admin_security = Security(authorise_current_redacted_user, scopes=admin_scopes.get_scope_array())
authenticated_admin_user = Annotated[RedactedUserInDB, admin_security]

# Ensure *all* admin endpoints are authenticated at the cost of potentially validating credentials twice
admin_router = APIRouter(prefix='/admin', tags=['Admin'], dependencies=[admin_security])

# TODO: Add explicit endpoint to ban IP from API usage, then add auto-ban after subsequent login failures/expired token usages
# TODO: Check if IP has been banned on API call (would be at app level)

@admin_router.post('/ip-ban')
async def blacklist_ip_from_api(token_user: authenticated_admin_user, ban_details: HarmfulIPAddressBanBody, session: AsyncSessionDep):
    user_id = (await session.exec(select(User.id).where(User.username == token_user.username))).one()
    if user_id is None:
        return bad_credentials_exception
    
    ban_end_date = None if ban_details.duration is None else get_utc_now() + ban_details.duration
    
    ban_entry = BannedIPAddress(ip=ban_details.ip, reason=ban_details.reason, created_by=user_id, ends_at=ban_end_date)
    session.add(ban_entry)
    await session.commit()
    
    return Response(status_code=status.HTTP_200_OK)

@admin_router.delete('/ip-ban')
async def remove_ip_from_api_blacklist():
    raise NotImplementedError()
    return Response(status_code=status.HTTP_200_OK)