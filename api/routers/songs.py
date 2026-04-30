
from typing import Annotated

from asyncpg import CheckViolationError, ForeignKeyViolationError, UniqueViolationError
from fastapi import APIRouter, HTTPException, Security, status
from fastapi.responses import Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import apaginate
from sqlmodel import or_, select
from sqlalchemy.exc import IntegrityError

from api.dependencies.auth.authentication import authorise_current_redacted_user
from api.utils.auth.scopes.fields import DBDeleteSubScope, DBReadSubScope, DBWriteSubScope
from api.utils.auth.scopes.scope_manager import ScopeManager, SongScopeField
from db.models.songs_and_charts import Song, SongArtist
from db.models.users import User
from db.session.session import AsyncSessionDep


song_router = APIRouter(prefix='/song', tags=['Songs'])

song_read_scopes = ScopeManager(song_access=SongScopeField(read_access=DBReadSubScope(granted=True))).get_scope_array()
song_write_scopes = ScopeManager(song_access=SongScopeField(write_access=DBWriteSubScope(granted=True))).get_scope_array()
song_delete_scopes = ScopeManager(song_access=SongScopeField(delete_access=DBDeleteSubScope(granted=True))).get_scope_array()

# TODO: Add more query params
@song_router.get("/")
async def get_song_page(
    current_user: Annotated[User, Security(authorise_current_redacted_user, scopes=song_read_scopes)],
    session: AsyncSessionDep,
    name:   str | None = None,
    artist_id: int | None = None,
    artist_name: str | None = None
) -> Page[Song]:
    song_query = select(Song).join(SongArtist, Song.artist_id == SongArtist.id)
    if name:
        song_query = song_query.where(or_(Song.name_en.contains(name), Song.name_jp.contains(name)))
    if artist_id:
        song_query = song_query.where(Song.artist_id == artist_id)
    if artist_name:
        song_query = song_query.where(or_(SongArtist.name_en.contains(artist_name), SongArtist.name_jp.contains(artist_name)))
        
    return await apaginate(session, song_query)

@song_router.post("/")
async def add_song(
    # current_user: Annotated[User, Security(authorise_current_redacted_user, scopes=song_write_scopes)],
    session: AsyncSessionDep,
    song: Song
):
    session.add(song)
    try:
        await session.commit()
    # except UniqueViolationError as unique_exc:
    #     print(unique_exc.sqlstate)
    # TODO: Separate generic integrity error and unique violation of custom rules
    except IntegrityError as integrity_exc:
        
        err_message = str(integrity_exc)
        
        # Check for custom unique constraints
        # TODO: Check if there is a way to extract unwrapped exception type instead of searching within the error message
        if 'unique_song_name_and_artist' in err_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'song name and artist combination already used - do not duplicate songs')
        if 'bpm_is_positive' in err_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'bpm must be > 0')
        
        # print(integrity_exc.orig)
        # if isinstance(integrity_exc.orig, AsyncpgIntegrityError):
        #     # integrity_exc.orig
        #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{unique_exc.sqlstate} song name and artist combination already used - do not duplicate songs')
        # print(type(integrity_exc.orig))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='id collision - check if song id is in use and relations')
        
    return Response(status_code=200)