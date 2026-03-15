from abc import ABC
from re import compile as compile_regex
from typing import ClassVar, override

from pydantic import BaseModel

from api.utils.auth.scopes.fields.interface import ScopeField, ScopeFieldWithSubScopes, SubScopeField, whitespace_pattern

class DBReadSubScope(SubScopeField):
    SubScopeName: ClassVar[str] = 'r'
    description: ClassVar[str] = 'Manages read access'
    
class DBWriteSubScope(SubScopeField):
    SubScopeName: ClassVar[str] = 'w'
    description: ClassVar[str] = 'Manages insertion and update access'
    
class DBDeleteSubScope(SubScopeField):
    SubScopeName: ClassVar[str] = 'd'
    description: ClassVar[str] = 'Manages deletion access'


class DBRecordScopeField(ScopeFieldWithSubScopes, ABC):
    """
    Encapsulates applicable database-related scopes for a single type of content.
    Used by the API to determine whether a user can read, write or delete certain content.
    """
    DocsName: ClassVar[str] = 'TODO'

    read_access:   DBReadSubScope   = DBReadSubScope()
    write_access:  DBWriteSubScope  = DBWriteSubScope()
    delete_access: DBDeleteSubScope = DBDeleteSubScope()
    
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