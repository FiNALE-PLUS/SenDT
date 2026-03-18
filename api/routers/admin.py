from typing import Annotated

from fastapi import APIRouter, Response, Security, status

from api.dependencies.auth.authentication import RedactedUserInDB, authorise_current_user
from api.utils.auth.scopes.fields.boolean_field import AdministratorScope
from api.utils.auth.scopes.scope_manager import ScopeManager

admin_scopes = ScopeManager(admin=AdministratorScope(granted=True))

admin_security = Security(authorise_current_user, scopes=admin_scopes.get_scope_array())
authenticated_admin_user = Annotated[RedactedUserInDB, admin_security]

# Ensure *all* admin endpoints are authenticated at the cost of potentially validating credentials twice
admin_router = APIRouter(prefix='/admin', tags=['Admin'], dependencies=[admin_security])

# TODO: Add explicit endpoint to ban IP from API usage, then add auto-ban after subsequent login failures/expired token usages
@admin_router.get('/ban-ip')
async def blacklist_ip_from_api():
    return Response(status_code=status.HTTP_200_OK)