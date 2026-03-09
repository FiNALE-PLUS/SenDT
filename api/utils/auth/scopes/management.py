from abc import ABC
from enum import StrEnum
from typing import ClassVar
from warnings import deprecated

from pydantic import BaseModel

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


class DBRecordScopeField(BaseModel, ABC):
    """
    Encapsulates applicable database-related scopes for a single type of content.
    Used by the API to determine whether a user can read, write or delete certain content.
    """
    FieldName: ClassVar[str] = 'TODO'

    # access_level: ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    read_access:   bool = False
    write_access:  bool = False
    delete_access: bool = False

    def get_scope_value(self) -> str | None:
        if not any((self.read_access, self.write_access, self.delete_access)):
            return None
        else:
            access_levels_string = f'{'r' if self.read_access else ''}{'w' if self.write_access else ''}{'d' if self.delete_access else ''}'
            return f'{self.FieldName}:{access_levels_string}'
    
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
        split = scope_string.split(':')
        
        scope_type = split[0]
        scopes = split[1]
        
        if len(split) != 2:
            raise ValueError('not a valid scope string')
        if scope_type != self.FieldName:
            raise ValueError('scope string not for this scope')
        if len(scopes) > 3 or len(scopes) < 1:
            raise ValueError('no scopes provided in string')
        
        # TODO: May need to instead be serialised and deserialised into separate space-separated scopes for individual scopes
        self.read_access = 'r' in scopes
        self.write_access = 'w' in scopes
        self.delete_access = 'd' in scopes
        
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
        
        scopes = token_scope_string.split(' ')
        
        for scope in scopes:
            try:
                self.try_from_string(scope)
                return
            except Exception:
                pass
        self.read_access = False
        self.write_access = False
        self.delete_access = False
        
        # raise ValueError('scope not found')
    
class SongScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'song'
    
class ChartScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'chart'
    
class ArtistScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'artist'
    
class ChartCreatorScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'creator'
    
class GenreScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'genre'
    
class SdtBlobScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'sdt'
    
class AudioScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'audio'
    
class VideoScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'video'

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
            self.__getattribute__(field_name).try_from_token_scope_string(token_scopes)
            

    def __str__(self):
        if self.admin:
            return 'admin'
        
        access_fields = []
        
        for field_name, _ in filter(lambda f: issubclass(f[1].annotation, DBRecordScopeField), self.__pydantic_fields__.items()):
            stringified_scope = self.__getattribute__(field_name).get_scope_value()
            if stringified_scope is not None:
                access_fields.append(stringified_scope)
        
        scopes = ' '.join(access_fields)

        if self.cross_edit_access:
            scopes += ' xedit'  # Probably faster than ' '.join()

        return scopes
