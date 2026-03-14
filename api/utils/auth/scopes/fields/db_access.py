from abc import ABC
from re import compile as compile_regex
from typing import ClassVar, override

from pydantic import BaseModel

from api.utils.auth.scopes.fields.interface import ScopeField

whitespace_pattern = compile_regex(r'\s')

class DBRecordSubScope(BaseModel, ABC):
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

class DBReadSubScope(DBRecordSubScope):
    SubScopeName: ClassVar[str] = 'r'
    description: ClassVar[str] = 'Manages read access'
    
class DBWriteSubScope(DBRecordSubScope):
    SubScopeName: ClassVar[str] = 'w'
    description: ClassVar[str] = 'Manages insertion and update access'
    
class DBDeleteSubScope(DBRecordSubScope):
    SubScopeName: ClassVar[str] = 'd'
    description: ClassVar[str] = 'Manages deletion access'


class DBRecordScopeField(ScopeField, ABC):
    """
    Encapsulates applicable database-related scopes for a single type of content.
    Used by the API to determine whether a user can read, write or delete certain content.
    """
    DocsName: ClassVar[str] = 'TODO'

    read_access:   DBReadSubScope   = DBReadSubScope()
    write_access:  DBWriteSubScope  = DBWriteSubScope()
    delete_access: DBDeleteSubScope = DBDeleteSubScope()
        
    @classmethod
    def get_string_for_subscope(cls, subscope: DBRecordSubScope):
        return f'{cls.ScopeName}:{subscope.__class__.SubScopeName}'
    
    @override
    def get_scope_values(self) -> list[str]:
        scope_values = []
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordSubScope), self.__pydantic_fields__.items()):
            sub_scope: DBRecordSubScope = self.__getattribute__(field_name)
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
        
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordSubScope), self.__pydantic_fields__.items()):
            subscope: DBRecordSubScope = self.__getattribute__(field_name)
            if subscope.get_subscope_string_with_scope(self.ScopeName) == scope_string:
                subscope.granted = True
                return
        
        return None
        
    def from_token_scope_string(self, token_scope_string: str) -> None:
        """
        A shorthand to simplify searching for a scope within a set of scopes provided by a JWT. 
        Matches the scopes found, including if none are found (in which case all scopes are set to ``False``).

        Args:
            token_scope_string (str): The set of scopes to search within.

        Returns:
            _type_: The deserialised scopes of the group represented by `token_scope_string`.
        """
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordSubScope), self.__pydantic_fields__.items()):
            subscope: DBRecordSubScope = self.__getattribute__(field_name)
            subscope.granted = False
        
        scopes = token_scope_string.split(' ')
        
        for scope in scopes:
            self.try_from_string(scope)
    
    @override
    def openapi_scope_descriptions(self) -> dict[str, str]:
        scope_descriptions = {}
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordSubScope), self.__pydantic_fields__.items()):
            subscope: DBRecordSubScope = self.__getattribute__(field_name)
            scope_descriptions[subscope.get_subscope_string_with_scope(self.ScopeName)] = f'{subscope.description} for {self.DocsName}(s)'
            
        
        return scope_descriptions
    
class SongScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 's'
    DocsName: ClassVar[str] = 'song'
    
class ChartScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'c'
    DocsName: ClassVar[str] = 'chart'
    
class ArtistScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'a'
    DocsName: ClassVar[str] = 'artist'
    
class ChartCreatorScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'cc'
    DocsName: ClassVar[str] = 'creator'
    
class GenreScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'g'
    DocsName: ClassVar[str] = 'genre'
    
class SdtBlobScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'sdt'
    DocsName: ClassVar[str] = 'SDT chart'
    
class AudioScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'aud'
    DocsName: ClassVar[str] = 'audio file'
    
class VideoScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'v'
    DocsName: ClassVar[str] = 'video file'