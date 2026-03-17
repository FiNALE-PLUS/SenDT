from typing import ClassVar, override

from api.utils.auth.scopes.fields.interface import ScopeField, ScopeFieldWithSubScopes, SubScopeField


class TOTPVerifySubScope(SubScopeField):
    SubScopeName: ClassVar[str] = 'v'
    description: ClassVar[str] = 'Manages ability to verify TOTP has been setup correctly '
    
class TOTPTokenSubScope(SubScopeField):
    SubScopeName: ClassVar[str] = 't'
    description: ClassVar[str] = 'Manages ability to use TOTP for login'

class TOTPScopeField(ScopeFieldWithSubScopes):
    ScopeName: ClassVar[str] = 'totp'
    DocsName: ClassVar[str]  = 'two-factor authentication'
    
    user_setup_verification_access: TOTPVerifySubScope = TOTPVerifySubScope()
    authenticate_access_token_access: TOTPTokenSubScope = TOTPTokenSubScope()
    
    