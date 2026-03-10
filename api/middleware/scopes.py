
from fastapi.security import OAuth2PasswordBearer

from api.utils.auth.scopes.management import ScopeManager

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token",
    # TODO
    scopes=ScopeManager().get_openapi_scope_docs()
)

# TODO: Add dependency to validate scopes as argument