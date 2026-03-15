from typing import ClassVar, override

from api.utils.auth.scopes.fields.interface import ScopeField


class TOTPScopeField(ScopeField):
    ScopeName: ClassVar[str] = 'totp'
    
    @override
    def get_scope_values(self) -> list[str]:
        ...
    
    @override
    def from_token_scope_string(self, token_scope_string: str) -> None:
        
        ...
        
    @override
    def openapi_scope_descriptions(self) -> dict[str, str]:
        ...