
from api.utils.auth.scopes.management import ArtistScopeField, ChartCreatorScopeField, ChartScopeField, DBReadSubScope, GenreScopeField, ScopeManager, SongScopeField


def get_scopes_for_role(role: str) -> ScopeManager:
    match role:
        case 'none':
            return ScopeManager()
        # The viewer role is expected to be given to guests that do not directly contribute to the project, and so are not given access to game content
        case 'viewer':
            return ScopeManager(
                song_access=SongScopeField(read_access=DBReadSubScope(granted=True)),
                chart_access=ChartScopeField(read_access=DBReadSubScope(granted=True)),
                artist_access=ArtistScopeField(read_access=DBReadSubScope(granted=True)),
                chart_creator_access=ChartCreatorScopeField(read_access=DBReadSubScope(granted=True)),
                genre_access=GenreScopeField(read_access=DBReadSubScope(granted=True)),
            )
        case 'dev':
            # TODO
            raise NotImplementedError()
        case 'admin':
            return ScopeManager(admin=True)
        case _:
            raise ValueError(f'role {role} not recognised')