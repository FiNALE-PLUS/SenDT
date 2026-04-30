
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
    current_user: Annotated[User, Security(authorise_current_redacted_user, scopes=song_write_scopes)],
    session: AsyncSessionDep,
    song: Song
):
    session.add(song)
    try:
        await session.commit()
    
    except IntegrityError as integrity_exc:
        
        # Constraints on DB
        err_message = str(integrity_exc)
        # print(err_message)
        # PK
        if 'song_pkey' in err_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='song id already in use')
        if 'song_artist_id_fkey' in err_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='song artist does not exist')
        if 'song_genre_id_fkey' in err_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='song genre does not exist')
        
        if 'unique_song_name_and_artist' in err_message:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='song name and artist combination already used - do not duplicate songs')
        if 'bpm_is_positive' in err_message:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='bpm must be > 0')
    
        # Unknown client error
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
        
    return Response(status_code=200)