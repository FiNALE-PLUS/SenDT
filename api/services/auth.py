from api.utils.auth.scopes.fields.db_access import (
    SongScopeField, ChartScopeField, ArtistScopeField, ChartCreatorScopeField, 
    GenreScopeField, SdtBlobScopeField, AudioBlobScopeField, VideoBlobScopeField
    )

from api.utils.auth.scopes.scope_manager import ScopeManager


class UnknownRole(ValueError):
    """
    Used to document an unknown role being given by a parent function to convert into permissions. 
    Indicates that the permission getter function is likely out-of date, 
    or that unauthorised edits to the DB may have been made.
    """
    ...

def get_scopes_for_role(role: str) -> ScopeManager:
    """
    Gets the OAuth scopes for a user role, generally passed to a JWT for future use within the API.

    Args:
        role (str): The name of the role to get scopes for.

    Raises:
        UnknownRole: If the given role is not known.

    Returns:
        ScopeManager: A manager containing the relevant scopes for the requested role.
    """
    match role:
        case 'none':
            # ``ScopeManager`` has no permissions by default
            return ScopeManager()
        case 'viewer':
            return ScopeManager(
                song_access=SongScopeField(read_access=True),
                chart_access=ChartScopeField(read_access=True),
                artist_access=ArtistScopeField(read_access=True),
                chart_creator_access=ChartCreatorScopeField(read_access=True),
                genre_access=GenreScopeField(read_access=True),
                sdt_blob_access=SdtBlobScopeField(read_access=True),
                audio_blob_access=AudioBlobScopeField(read_access=True),
                video_blob_access=VideoBlobScopeField(read_access=True)
            )
        case 'dev':
            return ScopeManager(
                
            )
        case 'admin':
            return ScopeManager(
                admin=True
            )
        case _:
            raise UnknownRole(role)