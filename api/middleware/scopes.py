
from fastapi.security import OAuth2PasswordBearer

from api.utils.auth.scopes.management import ScopeManager

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    # TODO
    scopes={
        'songs:read': 'read song data',
        'songs:write': 'write song data'
    }
)


def authorise_request(required_scopes: ScopeManager):
    ...