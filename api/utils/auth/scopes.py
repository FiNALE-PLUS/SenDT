from enum import StrEnum

from pydantic import BaseModel


class ScopeAccessLevel(StrEnum):
    read = 'read'
    write = 'write'
    delete = 'delete'
    all = 'all'
    none = 'none'

    def scope_stringify(self, scope_name):
        return ':'.join((scope_name, self.value))


class ScopeManager(BaseModel):
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
                scopes += ' xedit'

            return scopes
