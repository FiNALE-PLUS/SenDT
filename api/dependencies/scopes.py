from api.utils.auth.scopes.fields import DBReadSubScope
from api.utils.auth.scopes.fields.db_access import AudioBlobScopeField, DBWriteSubScope, SdtBlobScopeField, VideoBlobScopeField
from api.utils.auth.scopes.scope_manager import ArtistScopeField, ChartCreatorScopeField, ChartScopeField, GenreScopeField, ScopeManager, SongScopeField


def get_scopes_for_role(role: str) -> ScopeManager:
    match role:
        case 'none':
            return ScopeManager()
        # The viewer role is expected to be given to guests that do not directly contribute to the project, and so are not given access to game content
        case 'viewer':
            return ScopeManager(
                song_access          = SongScopeField(read_access=DBReadSubScope(granted=True)),
                chart_access         = ChartScopeField(read_access=DBReadSubScope(granted=True)),
                artist_access        = ArtistScopeField(read_access=DBReadSubScope(granted=True)),
                chart_creator_access = ChartCreatorScopeField(read_access=DBReadSubScope(granted=True)),
                genre_access         = GenreScopeField(read_access=DBReadSubScope(granted=True)),
            )
        case 'dev':
            # TODO
            return ScopeManager(
                song_access          = SongScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                chart_access         = ChartScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                artist_access        = ArtistScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                chart_creator_access = ChartCreatorScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                genre_access         = GenreScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                sdt_blob_access      = SdtBlobScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                audio_blob_access    = AudioBlobScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
                video_blob_access    = VideoBlobScopeField(read_access=DBReadSubScope(granted=True), write_access=DBWriteSubScope(granted=True)),
            )
        case 'admin':
            return ScopeManager(admin=True)
        case _:
            raise ValueError(f'role {role} not recognised')