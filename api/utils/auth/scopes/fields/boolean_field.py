from abc import ABC
from typing import ClassVar, override
from warnings import deprecated

from api.utils.auth.scopes.fields.interface import ScopeField


class BooleanScopeField(ScopeField, ABC):
    """
    Used to define scopes that can only be directly granted to a user token without any sub-scopes. 
    Ideal for situations where only one attribute needs to be described, such as whether a user is an administrator or not.
    """
    
    Documentation: ClassVar[str] = 'TODO'
    granted: bool                = False
    
    @override
    def get_scope_values(self) -> list[str]:
        if self.granted:
            return [self.ScopeName]
        else:
            return []
    
    @override
    def from_token_scope_string(self, token_scope_string: str) -> None:
        separated_scopes = token_scope_string.split(' ')
        self.granted = self.ScopeName in separated_scopes
    
    @override
    def openapi_scope_descriptions(self) -> dict[str, str]:
        return {self.ScopeName: self.Documentation}
    
    def __bool__(self):
        """
        Mild syntactic sugar to shorten checking a boolean scope's current status.

        Returns:
            bool: Whether the scope has been granted.
        """
        return self.granted


class CrossEditScope(BooleanScopeField):
    ScopeName: ClassVar[str] = 'xedit'
    Documentation: ClassVar[str] = 'Grants edit access to records owned by another user'
    

class AdministratorScope(BooleanScopeField):
    ScopeName: ClassVar[str] = 'admin'
    Documentation: ClassVar[str] = 'Bypasses all scope requirements'

@deprecated('Use TOTPScopeField instead')
class VerifyTwoFactorScope(BooleanScopeField):
    ScopeName: ClassVar[str] = 'totp:v'
    Documentation: ClassVar[str] = 'Grants permission to verify that TOTP 2FA has been correctly configured on a user\'s device'
