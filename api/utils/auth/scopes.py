from abc import ABC
from enum import StrEnum
from typing import ClassVar

from pydantic import BaseModel

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


# TODO: Alternative to method in ``ScopeManager``: https://stackoverflow.com/questions/70852331/how-to-define-class-attributes-after-inheriting-pydantics-basemodel#71664301
#  Use this as a more concrete way of parsing expected Scopes, migrate multiple scope per field management to this class
class DBRecordScopeField(BaseModel, ABC):
    FieldName: ClassVar[str] = 'TODO'

    # access_level: ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    read_access:   bool
    write_access:  bool
    delete_access: bool

    def get_scope_value(self) -> str | None:
        if not any((self.read_access, self.write_access, self.delete_access)):
            return None
        else:
            access_levels_string = \
            f'{'r' if self.read_access else ''}'
            f'{'w' if self.write_access else ''}'
            f'{'d' if self.delete_access else ''}'
            return f'{self.FieldName}:{access_levels_string}'
    
    @classmethod
    def try_from_string(cls, scope_string: str):
        """
        Attempts to look for a valid string representation of this scope, and returns it if available.
        
        Args:
            scope_string (str): The stringified scope to search.

        Raises:
            ValueError: _description_
            ValueError: _description_
            ValueError: _description_

        Returns:
            _type_: The deserialised scopes represented by `scope_string`
        """
        split = scope_string.split(':')
        
        scope_type = split[0]
        scopes = split[1]
        
        if len(split) != 2:
            raise ValueError('not a valid scope string')
        if scope_type != cls.FieldName:
            raise ValueError('scope string not for this scope')
        if len(scopes) > 3 or len(scopes) < 1:
            raise ValueError('no scopes provided in string')
        
        return cls(
            read_access='r' in scopes,
            write_access='w' in scopes,
            delete_access='d' in scopes
        )
        
    @classmethod
    def try_from_token_scope_string(cls, token_scope_string: str):
        """
        A shorthand to simplify searching for a scope within a set of scopes provided by a JWT.

        Args:
            token_scope_string (str): The set of scopes to search within.

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        
        scopes = token_scope_string.split(' ')
        
        for scope in scopes:
            try:
                return cls.try_from_string(scope)
            except Exception:
                pass
        
        raise ValueError('scope not found')
    
class SongScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'song'
    
class ChartScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'chart'
    
class ArtistScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'artist'
    
class ChartCreatorScopeField(DBRecordScopeField):
    FieldName: ClassVar[str] = 'chart_creator'
    
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

    song_access:          ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    chart_access:         ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    artist_access:        ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    chart_creator_access: ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    genre_access:         ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    sdt_blob_access:      ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    audio_blob_access:    ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none
    video_blob_access:    ScopeAccessLevel | set[ScopeAccessLevel] = ScopeAccessLevel.none

    cross_edit_access: bool = False
    admin: bool = False

    # TODO: Return a field based on key string? Abstract keys into another class?
    #  If the first solution, migrate ``access_keys`` in string constructor to use this function
    #  Alternatively move
    def field_from_key(self, key: str):
        ...

    def __str__(self):
        if self.admin:
            return 'admin'

        else:
            access_keys = {
                'song': self.song_access,
                'chart': self.chart_access,
                'artist': self.artist_access,
                'creator': self.chart_creator_access,
                'genre': self.genre_access,
                'sdt': self.sdt_blob_access,
                'audio': self.audio_blob_access,
                'video': self.video_blob_access,
            }

            access_names = []

            for access_name, access_level in access_keys.items():
                if isinstance(access_level, set):
                    if ScopeAccessLevel.all in access_level:
                        access_names.append(ScopeAccessLevel.all.scope_stringify(access_name))
                    elif ScopeAccessLevel.none not in access_level:
                        access_names.append(
                            ' '.join((level.scope_stringify(access_name) for level in access_level))
                            # ':'.join((access_name, access_level.value))
                        )
                else:
                    if access_level != ScopeAccessLevel.none:
                        access_names.append(access_level.scope_stringify(access_name))

            scopes = ' '.join(access_names)

            if self.cross_edit_access:
                scopes += ' xedit'  # Probably faster than ' '.join()

            return scopes
