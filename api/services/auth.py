from api.utils.auth.scopes import ScopeAccessLevel, ScopeManager


class UnknownRole(ValueError):
    """
    Used to document an unknown role being given by a parent function to convert into permissions. 
    Indicates that the permission getter function is likely out-of date, 
    or that unauthorisd edits to the DB may have been made.
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
                song_access=ScopeAccessLevel.read,
                chart_access= ScopeAccessLevel.read,
                artist_access=ScopeAccessLevel.read,
                chart_creator_access=ScopeAccessLevel.read,
                genre_access=ScopeAccessLevel.read,
                sdt_blob_access=ScopeAccessLevel.read,
                audio_blob_access=ScopeAccessLevel.read,
                video_blob_access=ScopeAccessLevel.read
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