from abc import ABC, abstractmethod
from re import compile as compile_regex
from typing import ClassVar, override

from pydantic import BaseModel


class ScopeField(BaseModel, ABC):
    ScopeName: ClassVar[str] = 'TODO'
    
    @abstractmethod
    def get_scope_values(self) -> list[str]:
        """
        Used to get a scope field's individual scope values. Scopes that only return a single scope must return a list containing said singular scope.

        Returns:
            list[str]: A list of all scope values that should be included within the ``scope`` field of the relevant JWT
        """
        ...
    
    @abstractmethod
    def from_token_scope_string(self, token_scope_string: str) -> None:
        """
        Mutates the scope field to match its state with any relevant scopes from a JWT. Accepts the value of the token's ``scope`` field as-is.

        Args:
            token_scope_string (str): The full ``scope`` value of the token to match scopes of.
        """
        ...
        
    @abstractmethod
    def openapi_scope_descriptions(self) -> dict[str, str]:
        """
        Generates a dictionary containing the scope names and descriptions for the current field to be inserted into authentication docs.

        Returns:
            dict[str, str]: A dictionary of keys representing the individual stringified scopes, and values designating the documentation for the respective scope.
        """
        ...
        

whitespace_pattern = compile_regex(r'\s')

        
class SubScopeField(BaseModel, ABC):
    SubScopeName: ClassVar[str] = 'TODO'
    description: ClassVar[str] = 'TODO'
    
    granted: bool = False
    
    def __bool__(self):
        return self.granted
    
    @classmethod
    def get_subscope_string_with_scope(cls, scope: str):
        if whitespace_pattern.match(scope):
            raise ValueError('Scope must not contain whitespace')
        return f'{scope}:{cls.SubScopeName}'
    
    
class ScopeFieldWithSubScopes(ScopeField, ABC):
    # TODO: Replace DB access scopes and 2FA scopes with implementations of this class.
    @classmethod
    def get_string_for_subscope(cls, subscope: SubScopeField):
        return f'{cls.ScopeName}:{subscope.__class__.SubScopeName}'
    
    @override
    def get_scope_values(self) -> list[str]:
        scope_values = []
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, SubScopeField), self.__pydantic_fields__.items()):
            sub_scope: SubScopeField = self.__getattribute__(field_name)
            if sub_scope.granted:
                scope_values.append(self.get_string_for_subscope(sub_scope))
        
        return scope_values
    
    def try_from_string(self, scope_string: str) -> None:
        """
        Attempts to look for a valid string representation of this scope, and mutates itself to match it if available.
        
        Args:
            scope_string (str): The stringified scope to search.

        Raises:
            ValueError: If the scope is not in a valid format to be deserialised.

        Returns:
            _type_: The deserialised scopes represented by `scope_string`.
        """
        if whitespace_pattern.match(scope_string):
            raise ValueError('This function is intended to search a single scope. Please use `from_token_scope_string` if you want to pass a whole token to parse.')
        
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, SubScopeField), self.__pydantic_fields__.items()):
            subscope: SubScopeField = self.__getattribute__(field_name)
            if subscope.get_subscope_string_with_scope(self.ScopeName) == scope_string:
                subscope.granted = True
                return
        
        return None
    
    @override
    def from_token_scope_string(self, token_scope_string: str) -> None:
        """
        A shorthand to simplify searching for a scope within a set of scopes provided by a JWT. 
        Matches the scopes found, including if none are found (in which case all scopes are set to ``False``).

        Args:
            token_scope_string (str): The set of scopes to search within.

        Returns:
            _type_: The deserialised scopes of the group represented by `token_scope_string`.
        """
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, SubScopeField), self.__pydantic_fields__.items()):
            subscope: SubScopeField = self.__getattribute__(field_name)
            subscope.granted = False
        
        scopes = token_scope_string.split(' ')
        
        for scope in scopes:
            self.try_from_string(scope)
    
    @override
    def openapi_scope_descriptions(self) -> dict[str, str]:
        scope_descriptions = {}
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, SubScopeField), self.__pydantic_fields__.items()):
            subscope: SubScopeField = self.__getattribute__(field_name)
            scope_descriptions[subscope.get_subscope_string_with_scope(self.ScopeName)] = f'{subscope.description} for {self.DocsName}(s)'
            
        
        return scope_descriptions