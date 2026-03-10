from abc import ABC
from enum import StrEnum
import re
from typing import ClassVar
from warnings import deprecated

from pydantic import BaseModel

whitespace_pattern = re.compile(r'\s')

@deprecated('Use ``DBRecordScopeField`` subclass')
class ScopeAccessLevel(StrEnum):
    """
    Enumerates the available access possibilities for a particular scope.
    """

    read = 'read'
    write = 'write'
    delete = 'delete'
    all = 'all'
    none = 'none'

    def scope_stringify(self, scope_name):
        return ':'.join((scope_name, self.value))
    
    
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

# class DBCrossAccessScope(DBRecordSubScope):
#     VariantName: ClassVar[str] = 'x'

class DBRecordScopeField(BaseModel, ABC):
    """
    Encapsulates applicable database-related scopes for a single type of content.
    Used by the API to determine whether a user can read, write or delete certain content.
    """
    ScopeName: ClassVar[str] = 'TODO'
    DocsName: ClassVar[str] = 'TODO'

    # access_level: ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    read_access:   DBReadSubScope   = DBReadSubScope()
    write_access:  DBWriteSubScope  = DBWriteSubScope()
    delete_access: DBDeleteSubScope = DBDeleteSubScope()
        
    @classmethod
    def get_string_for_subscope(cls, subscope: DBRecordSubScope):
        return f'{cls.ScopeName}:{subscope.__class__.SubScopeName}'
        
    def get_scope_values(self) -> list[str]:
        scope_values = []
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordSubScope), self.__pydantic_fields__.items()):
            subscope: DBRecordSubScope = self.__getattribute__(field_name)
            if subscope.granted:
                scope_values.append(self.get_string_for_subscope(subscope))
        
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
    DocsName: ClassVar[str] = 'sdt'
    
class AudioScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'aud'
    DocsName: ClassVar[str] = 'audio'
    
class VideoScopeField(DBRecordScopeField):
    ScopeName: ClassVar[str] = 'v'
    DocsName: ClassVar[str] = 'video'

# TODO: Use new scope fields
class ScopeManager(BaseModel):
    """
    Manages the OAuth scopes of an authenticated user. Scope levels ``none`` and ``all``
    override all other values when part of a set, either commiting the other scopes or replacing them respectively.
    ``cross_edit_access`` allows for edit access to records owned by other users to the extent of
    their own scope permissions, and ``admin`` is equivalent ao all permissions in all areas.
    """

    song_access:          SongScopeField         = SongScopeField()
    chart_access:         ChartScopeField        = ChartScopeField()
    artist_access:        ArtistScopeField       = ArtistScopeField()
    chart_creator_access: ChartCreatorScopeField = ChartCreatorScopeField()
    genre_access:         GenreScopeField        = GenreScopeField()
    sdt_blob_access:      SdtBlobScopeField      = SdtBlobScopeField()
    audio_blob_access:    AudioScopeField        = AudioScopeField()
    video_blob_access:    VideoScopeField        = VideoScopeField()

    cross_edit_access:    bool                   = False
    admin:                bool                   = False
    
    def match_token_string_scopes(self, token_scopes: str):
        # Reset permissions to then grant as found
        self.admin = False
        self.cross_edit_access = False
          
        # While the split isn't necessary as of writing, doing so now will prevent an accidental collision 
        # causing unwarranted permissions being given to users.
        seperate_scopes = token_scopes.split(' ')
        if 'admin' in seperate_scopes:
            self.admin = True
        if 'xedit' in seperate_scopes:
            self.cross_edit_access = True
        
        # Dynamically get all ``DBRecordScopeField``s, ensuring inclusion of any future fields as they are added
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordScopeField), self.__pydantic_fields__.items()):
            scope_field: DBRecordScopeField = self.__getattribute__(field_name)
            scope_field.from_token_scope_string(token_scopes)
            

    def __str__(self):
        if self.admin:
            return 'admin'
        
        access_fields = []
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordScopeField), self.__pydantic_fields__.items()):
            stringified_scopes = self.__getattribute__(field_name).get_scope_values()
            if stringified_scopes is not None:
                access_fields.extend(stringified_scopes)
        
        scopes = ' '.join(access_fields)

        if self.cross_edit_access:
            scopes += ' xedit'  # Probably faster than ' '.join()

        return scopes
    
    def get_openapi_scope_docs(self) -> dict[str, str]:
        docs_dict = {}
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordScopeField), self.__pydantic_fields__.items()):
            scope_field: DBRecordScopeField = self.__getattribute__(field_name)
            scope_docs = scope_field.openapi_scope_descriptions()
            
            docs_dict.update(scope_docs)
            
        return docs_dict
